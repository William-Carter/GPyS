import pygame
import math
import circleCalc
from pointsToEq import lineFunc
GCONSTANT = 0.00000000667408
GM = 398600.4418
SCALE = 80000
INC = 2000  # How many ms per frame (On Earth) - 20 is realtime
SOL = 299792458
pygame.font.init()
FONT = pygame.font.SysFont(None, 48)

windowHeight = 900
windowWidth = 1200
midHeight = windowHeight/2
midWidth = windowWidth/2
pygame.init()
window = pygame.display.set_mode(
    (windowWidth, windowHeight), pygame.DOUBLEBUF | pygame.HWSURFACE)
pygame.display.set_caption("GPyS")
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

    def onLoop(self):
        self.draw()


class Satellite:
    def __init__(self, idnum, planet, orbitHeight, startpos=0, color=(255, 0, 0)):

        self.planet = planet
        self.startpos = startpos  # Angle
        self.position = self.startpos  # Angle
        self.color = color
        self.orbitHeight = orbitHeight  # Meters
        self.id = idnum
        self.distanceFromCenterGraphical = (
            self.planet.radius+self.orbitHeight)/SCALE  # Meters

        self.distanceFromCenter = (
            self.planet.radius+self.orbitHeight)
        self.orbitalSpeed = math.sqrt(GCONSTANT*planet.mass/planet.radius)

        self.orbitalPeriod = math.sqrt(
            (4*math.pi**2*(
                self.planet.radius+self.orbitHeight) ** 3)/(GCONSTANT*self.planet.mass))*10000

        self.eccentricity = 0
        self.tFactor = math.sqrt(
            1-(2*GCONSTANT*self.planet.mass)/((self.orbitHeight+self.planet.radius)*SOL**2))

        self.lorentz = self.getLorentz()

        self.clock = 0.0

    def getPos(self):
        distanceFromCenter = self.distanceFromCenterGraphical
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

    def drawRadius(self, r):
        pygame.draw.circle(window, (127, 0, 200),
                           self.getPos(), r, 1)

    def updatePosition(self):
        self.position = (self.startpos+360 *
                         (((self.clock) % self.orbitalPeriod))/self.orbitalPeriod)

    def getLorentz(self):
        return math.sqrt((1-(self.orbitalSpeed**2/SOL**2)))

    def getTime(self):
        return self.clock/self.lorentz/self.tFactor

    def onLoop(self):
        self.clock += INC*self.lorentz*self.tFactor
        self.updatePosition()
        self.draw()


class Observer:
    def __init__(self, planet, startpos=0, altitude=0, color=(0, 255, 0)):
        self.planet = planet
        self.position = startpos
        self.color = color
        self.altitude = altitude
        self.clock = 0
        self.tFactor = math.sqrt(
            1-(2*GCONSTANT*self.planet.mass)/((self.altitude+self.planet.radius)*SOL**2))

    def getPos(self):
        distanceFromCenter = (self.planet.radius+self.altitude)/SCALE
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
        self.disconnectedSatellites = []
        for sat in satellites:
            connected = True
            posA = self.getPos()
            posB = sat.getPos()
            eqFunc = lineFunc(posA, posB)
            if posA > posB:
                temp = posA
                posA = posB
                posB = temp
            # The plus/minus 1 here is to avoid the code thinking that a signal touching the ground on the spot of the observer is impossible to see
            for i in range(int(posA[0])+1, int(posB[0])-1):
                if self.planet.findHeight((i, eqFunc(i)))*SCALE < self.planet.radius:
                    connected = False

            if connected:
                self.connectedSatellites.append(sat)

            elif not connected:
                self.disconnectedSatellites.append(sat)

    def drawSightLines(self):
        for item in self.connectedSatellites:
            pygame.draw.line(window, (0, 255, 0), self.getPos(), item.getPos())

        # for item in self.disconnectedSatellites:
           # pygame.draw.line(window, (255, 0, 0), self.getPos(), item.getPos())

    def getDistances(self):
        self.distances = {}
        for item in self.connectedSatellites:
            distance = math.sqrt((self.getPos()[0]-item.getPos()[0])**2 +
                                 (self.getPos()[1]-item.getPos()[1])**2)

            delay = distance*SCALE/SOL
            timestamp = item.getTime()-delay
            deltaT = self.clock/self.tFactor-timestamp
            distanceCalc = SOL*deltaT
            self.distances[item] = distanceCalc
            item.drawRadius(self.distances[item]/SCALE)

    def getGPSPosition(self):
        sat1 = list(self.distances.keys())[0]
        sat2 = list(self.distances.keys())[1]
        pos1 = [item*SCALE for item in sat1.getPos()]
        pos2 = [item*SCALE for item in sat2.getPos()]

        intersects = circleCalc.ri(
            self.distances[sat1], self.distances[sat2], pos1, pos2)

        if intersects == None:
            return None

        if self.planet.findHeight(intersects[0]) > self.planet.findHeight(intersects[1]):
            return intersects[1]

        else:
            return intersects[0]

    def onLoop(self, satList):
        self.clock += INC*self.tFactor
        self.establishConnections(satList)
        self.draw()
        self.drawSightLines()
        self.getDistances()
        gpsPosition = [i/SCALE for i in self.getGPSPosition()]
        print(circleCalc.calcDist(self.getPos(), gpsPosition))
        if not gpsPosition == None:
            pygame.draw.circle(window, (255, 0, 255),
                               gpsPosition, 3)


if __name__ == "__main__":
    earth = Earth()
    satList = []
    satNum = 5
    idCount = 0
    for i in range(satNum):
        idCount += 1
        satList.append(Satellite(idCount, earth, 20180000,
                                 (360/satNum)*i, (0, 0, 255)))

    mrObserver = Observer(earth, 0, 0)
    going = True
    satList[0].color = ((255, 0, 0))
    while going:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                going = False
        window.fill((0, 0, 0))
        earth.onLoop()
        for sat in satList:
            sat.onLoop()
        mrObserver.onLoop(satList)
        img = FONT.render(str(satList[0].clock), True, (255, 255, 255))
        window.blit(img, (0, 0))
        img = FONT.render(str(mrObserver.clock), True, (255, 255, 255))
        window.blit(img, (0, 20))

        pygame.display.update()
        clock.tick(50)
