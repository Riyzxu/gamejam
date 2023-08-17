import pygame


class Weapon:
    def __init__(self, player, pos=(0, 0), hitbox_size=(100, 10)):
        self.player = player
        self.rect_pos = list(pos)
        self.flip = False
        self.hitbox_size = list(hitbox_size)
        # self.hitbox = pygame.Rect(self.rect_pos, self.hitbox_size)

    # def damage(self, value, flip):
    #     self.flip = flip

    def rect(self):
        return pygame.Rect(self.rect_pos, self.hitbox_size)

    def update(self, pos, size):
        self.rect_pos[1] = pos[1]
        if not self.flip:
            self.rect_pos[0] = pos[0] - self.hitbox_size[0]
        else:
            self.rect_pos[0] = pos[0] + size[1]


