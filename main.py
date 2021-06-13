import pygame
import math
from pointsToEq import lineFunc
from pygame import draw
import random
GCONSTANT = 0.00000000667408
GM = 398600.4418
SCALE = 80000
INC = 2000  # How many ms per frame (50fps)

windowHeight = 900
windowWidth = 1200
midHeight = windowHeight/2
midWidth = windowWidth/2
pygame.init()
window = pygame.display.set_mode(
    (windowWidth, windowHeight), pygame.DOUBLEBUF | pygame.HWSURFACE)
pygame.display.set_caption("GPS")
clock = pygame.time.Clock()


class Earth:
    def __init__(self):
        self.position = (midWidth, midHeight)
        self.radius = 6371000
        self.mass = 5.972*(10**24)
        self.clock = 0

    def findHeight(self, point):
        return math.sqrt((self.position[0]-point[0])**2 +
                         (self.position[1]-point[1])**2)

    def draw(self):
        pygame.draw.circle(window, (0, 0, 230),
                           self.position, self.radius/SCALE)


class Satellite:
    def __init__(self, planet, orbitHeight, startpos=0, color=(255, 0, 0)):

        self.planet = planet
        self.startpos = startpos
        self.position = self.startpos
        self.color = color
        self.orbitHeight = orbitHeight
        self.distanceFromCenter = (self.planet.radius+self.orbitHeight)/SCALE
        self.orbitalSpeed = math.sqrt(GCONSTANT*planet.mass/planet.radius)
        self.orbitalPeriod = 2*math.pi * \
            math.sqrt((self.distanceFromCenter**3)/GM)*60*1000
        self.eccentricity = 0

        self.clock = 0

    def getPos(self):
        distanceFromCenter = self.distanceFromCenter
        return (
            math.cos(math.radians(self.position))*distanceFromCenter +
            self.planet.position[0],
            math.sin(math.radians(self.position))*distanceFromCenter +
            self.planet.position[1]
        )

    def draw(self):
        drawPos = self.getPos()
        pygame.draw.circle(window, self.color,
                           drawPos, 5)

    def updatePosition(self):
        self.position = (self.startpos+360*self.clock/self.orbitalPeriod)

    def onLoop(self):
        self.clock += INC
        self.updatePosition()
        self.draw()


class Observer:
    def __init__(self, planet, startpos=0, color=(0, 255, 0)):
        self.planet = planet
        self.position = startpos
        self.color = color

    def getPos(self):
        distanceFromCenter = self.planet.radius/SCALE
        return (
            math.cos(math.radians(self.position))*distanceFromCenter +
            self.planet.position[0],
            math.sin(math.radians(self.position))*distanceFromCenter +
            self.planet.position[1]
        )

    def draw(self):
        drawPos = self.getPos()
        pygame.draw.circle(window, self.color,
                           drawPos, 5)

    def establishConnections(self, satellites):
        self.connectedSatellites = []
        for sat in satellites:
            connected = False
            posA = self.getPos()
            posB = sat.getPos()
            eqFunc = lineFunc(posA, posB)
            for i in range(int(posA[0]), int(posB[0])):
                if self.planet.findHeight((i, eqFunc(i))) < self.planet.radius:
                    connected = True

            if connected:
                self.connectedSatellites.append(sat)

    def drawSightLines(self):
        for item in self.connectedSatellites:
            pygame.draw.line(window, (0, 255, 0), self.getPos(), item.getPos())

    def onLoop(self, satList):
        self.establishConnections(satList)
        self.draw()
        self.drawSightLines()


class Transmission:
    def __init__(self, sender, receiver):
        self.sender = sender
        self.receiver = receiver

    def draw(self):
        pass


if __name__ == "__main__":
    earth = Earth()
    satList = []
    for i in range(8):
        satList.append(Satellite(earth, random.randint(
            10000000, 20180000), 45*i, (0, 0, 255)))

    mrObserver = Observer(earth)
    going = True
    satList[0].color = ((255, 0, 0))
    while going:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                going = False
        window.fill((0, 0, 0))
        earth.draw()
        for sat in satList:
            sat.onLoop()
        mrObserver.onLoop(satList)
        pygame.display.update()
        clock.tick(50)
