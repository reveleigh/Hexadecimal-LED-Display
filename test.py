def getPlace(r,g,b):
    p1 = r // 16
    p2 = r % 16
    p3 = g // 16
    p4 = g % 16
    p5 = b // 16
    p6 = b % 16
    return p1, p2, p3, p4, p5, p6

print(getPlace(243, 189, 254)[0])