a = [(0, 2), (1, 1), (1, 3)]

adjust = 0
for i in range(len(a)-1):
    adjust = 0
    for j in range(i+1, len(a)):
        if abs(a[i][0] - a[j][0]) + abs(a[i][1] - a[j][1]) == 1:
            adjust += 1
    print(adjust)