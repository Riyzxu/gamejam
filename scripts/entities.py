import math
import random
import pygame
from scripts.weapon import Weapon


class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}

        self.action = ''
        self.anim_offset = (0, 0)
        self.flip = False
        self.set_action('idle')

        self.last_movement = [0, 0]

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()

    def update(self, tilemap, movement=(0, 0)):
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}

        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])

        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                self.pos[0] = entity_rect.x

        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y

        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True

        self.last_movement = movement

        self.velocity[1] = min(5, self.velocity[1] + 0.1)

        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0

        self.animation.update()

    def render(self, surf, offset=(0, 0)):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False),
                  (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))


class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size)

        self.gun = Weapon(self, hitbox_size=(100, 10))

        self.air_time = 0
        self.jumps = 1
        self.shooting = False
        self.signals = {}
        self.gravity = True
        self.rope_check = None

    def update(self, tilemap, movement=(0, 0)):
        self.anim_offset = [0, 0]
        if self.animation.frame in {2, 10} and self.action == 'shoot':
            self.game.screenshake = max(10, self.game.screenshake)
            self.game.sfx['shoot'].play()
            # print(self.animation.frame)

        super().update(tilemap, movement=movement)

        self.air_time += 1

        if self.air_time > 120 and self.gravity:
            if not self.game.dead:
                self.game.screenshake = max(16, self.game.screenshake)

        if self.collisions['down']:
            self.air_time = 0
            self.jumps = 1

        if pygame.mouse.get_pos()[0] < self.game.screen.get_width() // 2:
            self.flip = True
        else:
            self.flip = False

        if not self.gravity:
            self.velocity[1] = 0
            self.air_time = 0
            self.set_action('climb')
        elif self.air_time > 4:
            self.set_action('jump')
        elif self.shooting:
            self.set_action('shoot')
            self.gun.update(self.pos.copy())
            if self.flip:
                self.gun.damage(10, False)
                self.anim_offset = [-9, -1]
            else:
                self.gun.damage(10, True)
                self.anim_offset = [-3, -1]
        elif movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')

        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] - 0.1, 0)
        else:
            self.velocity[0] = min(self.velocity[0] + 0.1, 0)

        # check if the tile the player is standing on is a rope
        self.rope_check = tilemap.entity_check((self.rect().centerx, self.rect().centery), 'rope')
        if self.rope_check:
            self.send_signal('on_rope')
        else:
            self.remove_signal('on_rope')
            self.gravity = True

    def render(self, surf, offset=(0, 0)):
        super().render(surf, offset=offset)

    def disable_gravity(self):
        self.gravity = False

    def remove_signal(self, name, value=False):
        try:
            del self.signals[name]
        except KeyError:
            pass

    def send_signal(self, name, value=True):
        self.signals[name] = True

    def signal_manager(self):
        return self.signals, self.rope_check

    def render_hitbox(self, surf, offset=(0, 0)):
        if self.flip:
            surf.blit(self.gun.hitbox, (self.pos[0] - offset[0] - self.gun.hitbox_size[0], self.pos[1] - offset[1]))
        else:
            surf.blit(self.gun.hitbox, (self.pos[0] - offset[0] + self.size[1], self.pos[1] - offset[1]))

    def jump(self):
        if not self.gravity:
            self.velocity[1] = -3
            self.gravity = True
            self.air_time = 5
            return True
        if self.jumps:
            self.velocity[1] = -3
            self.jumps -= 1
            self.air_time = 5
            return True

    def is_shooting(self):
        return self.shooting

    def shoot(self, value):
        self.shooting = value
