import math


def ri(cr1, cr2, cp1, cp2):
    int1 = [0, 0]
    int2 = [0, 0]
    distanceBetween = calcDist(cp1, cp2)
    if distanceBetween > cr1+cr2:
        return None

    if distanceBetween == 0 and cr1 == cr2:
        return None

    if distanceBetween < abs(cr1-cr2):
        return None

    a = (cr1**2 - cr2**2 + distanceBetween**2)/(2*distanceBetween)
    h = math.sqrt(cr1**2-a**2)
    p3 = [0, 0]
    p3[0] = cp1[0]+(a/distanceBetween)*(cp2[0]-cp1[0])
    p3[1] = cp1[1]+(a/distanceBetween)*(cp2[1]-cp1[1])
    int1[0] = p3[0]+(h/distanceBetween)*(cp2[1]-cp1[1])
    int1[1] = p3[1]-(h/distanceBetween)*(cp2[0]-cp1[0])

    int2[0] = p3[0]-(h/distanceBetween)*(cp2[1]-cp1[1])
    int2[1] = p3[1]+(h/distanceBetween)*(cp2[0]-cp1[0])

    return (int1, int2)


def calcDist(p1, p2):
    return math.sqrt((p2[0] - p1[0]) ** 2 +
                     (p2[1] - p1[1]) ** 2)
