import cv2
import numpy as np
import random

STROKES = 32

height = width = 256

image = np.zeros((height,width,3), np.uint8)
image[:,] = (255,255,255)

line = cv2.imread('stroke.png')

def draw_line(position: tuple, length: int, flipped = False):
    size = (length, line.shape[0])
    resized_line = cv2.resize(line, size, interpolation=cv2.INTER_LINEAR)
    for i in range(resized_line.shape[0]):
        for j in range(resized_line.shape[1]):
            if flipped:
                x = (position[0]+j) % width
                y = (position[1]+i) % height
                j = (resized_line.shape[1] - j - 1)
            else:
                x = (position[0]+i) % width
                y = (position[1]+j) % height
            value = min(image[x,y][0], resized_line[i][j][2])
            image[x,y] = (value, value, value)

for _ in range(STROKES):
    x = random.randint(0, width)
    y = random.randint(0, height)
    length = random.randint(int(0.3*width), width)
    draw_line((x, y), length, flipped=True)

cv2.imshow("A New Image", image)
cv2.waitKey(0)
