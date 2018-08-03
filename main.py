import pyglet
import numpy as np
import math
import random as rd


class Circle:
    def __init__(self, center, radius, batch, grp=None, color=(0, 0, 0), fill=True):

        self.center = list(center)
        self.radius = radius
        #
        self.batch = batch
        self.grp = grp
        self.color = color
        self.fill = fill

        self.makeVertices()

    def makeVertices(self):

        self.nbPoints = round(2 * np.pi * self.radius)

        s = np.sin(2 * np.pi / self.nbPoints)
        c = np.cos(2 * np.pi / self.nbPoints)

        dx, dy = self.radius, 0

        tmp = np.zeros((self.nbPoints * 2,))

        for x in range(0, self.nbPoints * 2, 2):
            tmp[x:x + 2] = self.center + np.array([dx, dy])
            dx, dy = (dx * c - dy * s), (dy * c + dx * s)

        self.vertex = self.batch.add(self.nbPoints,
                                     pyglet.gl.GL_TRIANGLE_FAN if self.fill else pyglet.gl.GL_LINE_LOOP,
                                     self.grp,
                                     ('v2f', tmp),
                                     ('c3B', self.color * self.nbPoints))

    def translation(self, dx, dy):

        self.center[0] += dx
        self.center[1] += dy

        for k in range(self.nbPoints):
            self.vertex.vertices[2 * k] += dx
            self.vertex.vertices[(2 * k) + 1] += dy


class Link:
    def __init__(self, p0, p1, couple, batch, grp=None, color=(0, 0, 0)):
        self.p0 = p0
        self.p1 = p1
        self.couple = couple
        #
        self.batch = batch
        self.grp = grp
        self.color = color

        pyglet.gl.glLineWidth(2)

        self.makeVertices()

    def makeVertices(self):
        tmp = self.p0 + self.p1

        self.vertex = self.batch.add(2,
                                     pyglet.gl.GL_LINES,
                                     self.grp,
                                     ('v2f/stream', tmp),
                                     ('c3B/stream', [255] * 6))

    def update(self, p0, p1):
        self.p0 = p0
        self.p1 = p1

        self.vertex.vertices = p0 + p1

        ## couleur
        distance = math.sqrt((p0[0] - p1[0]) ** 2 + (p0[1] - p1[1]) ** 2)
        l = 150

        if distance > l:
            self.vertex.vertices = [0, 0, 0, 0]
        else:

            plageGris = 35
            color = (255 - plageGris) + round(plageGris * (distance / l))
            self.vertex.colors = [color] * 6


class window(pyglet.window.Window):
    def __init__(self, width=400, height=400):
        platform = pyglet.window.get_platform()
        display = platform.get_default_display()
        screen = display.get_default_screen()

        screen_width = screen.width
        screen_height = screen.height

        # on init la fenetre
        super(window, self).__init__(screen=screen,
                                     width=width,
                                     height=height,
                                     vsync=False)

        # on le met la fenetre au centre de l'ecran
        self.set_location((screen_width - self.width) // 2,
                          (screen_height - self.height) // 2)

        # background color
        pyglet.gl.glClearColor(1, 1, 1, 1)

        self.batch = pyglet.graphics.Batch()
        self.bgs = []


    def on_draw(self):
        self.clear()
        self.batch.draw()

    def start(self):
        self.dots = []
        self.directions = []
        self.radiuses = []

        self.bg0 = pyglet.graphics.OrderedGroup(0)
        self.bg1 = pyglet.graphics.OrderedGroup(1)

        nbPoint = 64

        for i in range(nbPoint):
            self.bgs.append(pyglet.graphics.OrderedGroup(len(self.bgs)))

            ##### prms of the dot
            radius = 2 + rd.randrange(3)

            pos = (rd.randrange(self.width),
                   rd.randrange(self.height))

            angle = 2 * math.pi * rd.random()

            v = rd.choice([1 + i * 0.1 for i in range(10)])
            direction = [v * np.cos(angle), v * np.sin(angle)]

            dot = Circle(pos,
                         radius,
                         self.batch,
                         grp=self.bgs[-1],
                         color=(180, 180, 180),
                         fill=True)

            self.dots.append(dot)
            self.directions.append(direction)
            self.radiuses.append(radius)

        self.links = []
        for y in range(nbPoint - 1):  # (32-1):
            for z in range(y + 1, nbPoint):
                link = Link(self.dots[y].center, self.dots[z].center, (y, z), self.batch)
                self.links.append(link)

    def update(self, dt):

        for i in range(len(self.dots)):
            # condition de sortie

            px = self.dots[i].center[0]
            py = self.dots[i].center[1]

            # print(px, py)

            if not (self.radiuses[i] < px < self.radiuses[i] + self.width):
                self.directions[i][0] *= -1
            if not (self.radiuses[i] < py < self.radiuses[i] + self.width):
                self.directions[i][1] *= -1

            # translation
            self.dots[i].translation(self.directions[i][0], self.directions[i][1])

        for link in self.links:
            p0 = self.dots[link.couple[0]]
            p1 = self.dots[link.couple[1]]

            link.update(p0.center, p1.center)


if __name__ == '__main__':
    main = window(width=800, height=800)
    main.start()

    pyglet.clock.schedule_interval(main.update, 1 / 60)
    pyglet.app.run()
