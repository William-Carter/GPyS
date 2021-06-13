def lineFunc(pointA, pointB):
    gradient = (pointB[1]-pointA[1])/(pointB[0]-pointA[0])
    intercept = pointA[1]-pointA[0]*gradient

    def func(x):
        return gradient * x + intercept

    return func
