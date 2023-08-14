import random
import math


class Star:
    def __init__(self, pos, img, speed, depth):
        self.pos = list(pos)
        self.img = img
        self.speed = speed
        self.depth = depth

    def update(self):
        self.pos[0] += self.speed

    def render(self, surf, offset=(0, 0)):
        render_pos = (self.pos[0] - offset[0] * self.depth, self.pos[1] - offset[1] * self.depth)
        surf.blit(self.img, (render_pos[0] % (surf.get_width() + self.img.get_width()) - self.img.get_width(),
                             render_pos[1] % (surf.get_height() + self.img.get_height()) - self.img.get_height()))


class Stars:
    def __init__(self, star_images, count=16):
        self.stars = []

        for i in range(count):
            self.stars.append(Star((random.random() * 99999, random.random() * 99999), random.choice(star_images),
                                     0, random.random() * 0.6 + 0.2))

        self.stars.sort(key=lambda x: x.depth)

    def update(self):
        for star in self.stars:
            star.update()

    def render(self, surf, offset=(0, 0)):
        for star in self.stars:
            star.render(surf, offset=offset)