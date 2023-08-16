import time

import pygame
import sys
import random

from scripts.entities import Player
from scripts.tilemap import Tilemap
from scripts.utils import Animation, load_image, load_images
from scripts.stars import Stars
from scripts.dust import Dusts


class Game:
    def __init__(self):
        pygame.init()
        pygame.mouse.set_visible(False)

        pygame.display.set_caption('Risk of Lame')
        self.screen = pygame.display.set_mode((854, 480))
        self.outline_display = pygame.Surface((427, 240), pygame.SRCALPHA)
        self.display = pygame.Surface((427, 240))

        self.clock = FPS()

        self.movement = [False, False]
        self.vertical_movement = [False, False]

        self.assets = {
            'default': load_images('tiles/default'),
            'grass': load_images('tiles/grass'),
            'pillar': load_images('tiles/pillar'),
            'platform': load_images('tiles/platform'),
            'rope': load_images('tiles/rope'),
            'player/idle': Animation(load_images('entities/player/idle')),
            'player/run': Animation(load_images('entities/player/run'), img_dur=5),
            'player/jump': Animation(load_images('entities/player/jump')),
            'player/shoot': Animation(load_images('entities/player/shoot'), img_dur=6),
            'player/climb': Animation(load_images('entities/player/climb'), img_dur=10),
            'background': load_image('background.png'),
            'stars': load_images('stars'),
            'dust': load_images('dust'),
            'cursor': load_image('cursor.png'),

        }

        self.sfx = {
            'shoot': pygame.mixer.Sound('data/sfx/shoot.wav'),
        }

        self.cursor_img_rect = self.assets['cursor'].get_rect()

        self.player = Player(self, (0, 0), (6, 11))
        self.tilemap = Tilemap(self, tile_size=16)

        self.stars = Stars(self.assets['stars'], count=32)
        self.dust = Dusts(self.assets['dust'], count=32)

        self.leaf_spawners = []
        self.enemies = []

        self.scroll = [0, 0]
        self.dead = 0
        self.level = 0

        self.load_level(self.level)
        self.screenshake = 0
        self.near_rope = False
        self.on_rope = False
        self.current_rope = {}

    def load_level(self, map_id):
        self.tilemap.load('data/maps/' + str(map_id) + '.json')

        # self.leaf_spawners = []
        # for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
        #     self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))
        #
        # self.enemies = []
        # for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1)]):
        #     if spawner['variant'] == 0:
        #         self.player.pos = spawner['pos']
        #         self.player.air_time = 0
        #     else:
        #         self.enemies.append(Enemy(self, spawner['pos'], (8, 15)))

        for spawner in self.tilemap.extract([('spawners', 0)]):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
                self.player.air_time = 0

        self.scroll[0] += self.player.rect().centerx - self.display.get_width() / 2
        self.scroll[1] += self.player.rect().centery - self.display.get_height() / 2
        self.dead = 0

    def run(self):
        while True:
            self.near_rope = False
            self.outline_display.fill((0, 0, 0, 0))
            # self.display.blit(self.assets['background'], (0, 0))
            self.display.fill((35, 39, 42))

            if self.dead:
                self.dead += 1
                if self.dead > 40:
                    self.load_level(self.level)

            self.screenshake = max(0, self.screenshake - 1)

            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 30
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            self.stars.update()
            self.stars.render(self.display, offset=render_scroll)
            self.dust.update()
            self.dust.render(self.display, offset=render_scroll)

            self.tilemap.render(self.outline_display, offset=render_scroll)

            if not self.dead:
                # if self.player.is_shooting():
                #     self.player.render_hitbox(self.display, offset=render_scroll)

                self.player.update(
                    self.tilemap,
                    ((self.movement[1] - self.movement[0]) if not self.on_rope else 0, (self.vertical_movement[1] - self.vertical_movement[0]))
                )
                self.player.render(self.outline_display, offset=render_scroll)

                signals, self.current_rope = self.player.signal_manager()

                for signal in signals:
                    match signal:
                        case "on_rope":
                            self.near_rope = True

            display_mask = pygame.mask.from_surface(self.outline_display)
            display_sillhoutte = display_mask.to_surface(setcolor=(0, 0, 0, 50), unsetcolor=(0, 0, 0, 0))
            for offset in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                self.display.blit(display_sillhoutte, offset)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.player.shoot(True)

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.player.shoot(False)

                if event.type == pygame.KEYDOWN:
                    if self.near_rope and event.key == pygame.K_w:
                        self.player.pos[0] = self.current_rope['pos'][0] * 16 + 4
                        self.on_rope = True
                        self.player.disable_gravity()

                    if event.key == pygame.K_SPACE:
                        if self.player.jump():
                            self.on_rope = False
                            # self.sfx['jump'].play()

                    if event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_d:
                        self.movement[1] = True
                    if self.on_rope:
                        if event.key == pygame.K_w:
                            self.vertical_movement[0] = True
                        if event.key == pygame.K_s:
                            self.vertical_movement[1] = True

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_d:
                        self.movement[1] = False

                    if event.key == pygame.K_w:
                        self.vertical_movement[0] = False
                    if event.key == pygame.K_s:
                        self.vertical_movement[1] = False

                    if not self.on_rope:
                        self.vertical_movement = [False, False]


            screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2,
                                  random.random() * self.screenshake - self.screenshake / 2)

            self.display.blit(self.outline_display, (0, 0))
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), screenshake_offset)

            self.cursor_img_rect.center = pygame.mouse.get_pos()
            self.screen.blit(self.assets['cursor'], self.cursor_img_rect)
            self.clock.render(self.screen)

            pygame.display.update()
            self.clock.clock.tick(60)


class FPS:
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font("data/font.ttf", 34)
        self.text = self.font.render(str(self.clock.get_fps()), True, (0, 0, 0, 100))

    def render(self, display):
        self.text = self.font.render(str(int(self.clock.get_fps())), False, (255, 255, 255, 100))
        display.blit(self.text, (10, 5))


Game().run()
