import cv2
import numpy as np
import random
from typing import List, Tuple
from scipy.ndimage import rotate
from PIL import Image
from matplotlib import pyplot as plt
import time

# How many tone levels should be generated?
TONE_LEVELS = 6
TONE_STEP = 1/TONE_LEVELS

# Show a real time plot of the image as it is being generated?
PLOT_IMAGE = True

MIN_CANDIDATES = 100
MAX_CANDIDATES = 1000

PYRAMID_MIN_LEVEL = 1
K_SIZE = (9, 9)

ROT_DEG = 2

# In pixels; how big should the largest texture level be?
TEXTURE_SIZE = 256
TEXTURE_LEVELS = 4

stroke_texture = cv2.imread('stroke.png')
stroke_img = Image.open('stroke.png')


def create_texture(size: int) -> np.array:
    """
    Creates an empty (==fully white) image texture of the given dimensions.
    @param size: The side length of the texture.
    """
    image = np.zeros((size,size,3), np.uint8)
    image[:,] = (255,255,255)
    return image


def draw_stroke(img, stroke: Tuple[float, float, float], rotated = False) -> np.array:
    """
    Takes in a single image and draws a new stroke on it.
    @param img: The image to draw the stroke to.
    @param stroke: The stroke to draw.
    @param rotated: Whether the stroke should be rotated.
    """
    (width, height, _) = img.shape
    stroke_length = int(stroke[2] * width)
    stroke_x = int(stroke[0] * width)
    stroke_y = int(stroke[1] * height)
    
    size = (stroke_length, stroke_texture.shape[0])
    resized_stroke = cv2.resize(stroke_texture, size, interpolation=cv2.INTER_LINEAR)
    resized_stroke = rotate(resized_stroke, random.uniform(-ROT_DEG, ROT_DEG), mode="constant", cval=255, reshape=True, order=1)
    resized_stroke = np.pad(resized_stroke, ((0, width - resized_stroke.shape[0]), (0, height - resized_stroke.shape[1]), (0,0)), 'constant', constant_values=(255, 255))
    if rotated:
        resized_stroke = resized_stroke.transpose((1, 0, 2))
    resized_stroke = np.roll(resized_stroke, int( resized_stroke.shape[0]/2 ), axis=0)
    resized_stroke = np.roll(resized_stroke, int( resized_stroke.shape[1]/2 ), axis=1)
    resized_stroke = np.roll(resized_stroke, stroke_x, axis=0)
    resized_stroke = np.roll(resized_stroke, stroke_y, axis=1)
    np.minimum(img, resized_stroke, out=img)


def generate_stroke() -> Tuple[float, float, float]:
    return (
        random.random(),            # X position
        random.random(),            # Y position
        random.random()*0.7 + 0.3,  # Length, between 30%-100% of the image width.
    )


def compute_goodness(imgs: List[np.array], stroke: Tuple[float, float, float], pre_tone: List[float], rotated = False) -> float:
    """
    Check the goodness of the images passed in.
    @param imgs: The images to check the goodness of.
    @param stroke: The stroke to check the goodness of.
    @param pre_tone: The tone of the images before the stroke was added.
    @param rotated: Whether the stroke should be rotated.
    @return: The goodness of the images.
    """
    tone_sum = 0
    for (i, img) in enumerate(imgs):
        draw_stroke(img, stroke, rotated)
        pyramid_levels = i + 1 + PYRAMID_MIN_LEVEL
        for _ in range(pyramid_levels):
            # tone_sum += get_tone(cv2.GaussianBlur(img, K_SIZE, 0)) - pre_tone[i]
            tone_sum += get_tone(img) - pre_tone[i]
            img = cv2.pyrDown(img)
    tone_sum /= stroke[2]
    return -tone_sum


def copy_imgs(imgs: List[np.array]) -> List[np.array]:
    return [np.copy(img) for img in imgs]


def add_stroke(imgs: List[np.array], candidates: int = 1000, rotated = False):
    """
    Generates stroke candidates, evaluates the best one, draws it to the images.
    @param imgs: The images to draw the stroke to.
    @param candidates: How many stroke candidates to generate.
    @param rotated: Whether the stroke should be rotated.
    """
    # TODO: add support for generating strokes in both directions.
    strokes = []
    pre_tone = [get_tone(img) for img in imgs]
    for _ in range(candidates):
        stroke = generate_stroke()
        copied = copy_imgs(imgs)
        goodness = compute_goodness(copied, stroke, pre_tone, rotated)
        strokes.append((stroke, goodness))
    # Sort on goodness and return best one.
    strokes.sort(key=lambda x: x[1], reverse=True)
    best_stroke = strokes[0][0]
    for img in imgs:
        draw_stroke(img, best_stroke, rotated)


def get_tone(img: np.array) -> float:
    """
    Calculates average tone of a given image.
    @param img: The image to calculate the tone of.
    @return: The average tone of the image.
    """
    return np.mean(img) / 255


def reach_tone(imgs: List[np.array], tone: float):
    """
    Keeps adding strokes to each image level until the desired tone is reached.
    @param imgs: The different levels for a given tone.
    @param tone: The desired tone of the images.
    """
    last_draw = 0
    for (i, img) in enumerate(imgs):
        current_tone = get_tone(img)
        while current_tone > tone:
            current_tone = get_tone(img)
            candidates = MIN_CANDIDATES + (MAX_CANDIDATES - MIN_CANDIDATES) * (current_tone - tone) / current_tone
            add_stroke(imgs[i:], int(candidates), tone < 0.5)
            print(f"current_tone: {current_tone}")
            now = time.time()
            if PLOT_IMAGE and abs(now - last_draw) > 0.5:
                last_draw = now
                plt.imshow(imgs[len(imgs) - 1], interpolation='nearest')
                plt.draw()
                plt.pause(0.01)


if __name__ == '__main__':
    # Generate different LOD texture levels...
    imgs = []
    for i in range(TEXTURE_LEVELS):
        imgs.insert(0, create_texture(TEXTURE_SIZE // 2**i))
    # Generate each tone level...
    for i in range(1, TONE_LEVELS):
        target_tone = 1 - i * TONE_STEP
        print(f'Generating image texture {target_tone}')
        reach_tone(imgs, target_tone)
        for (x, img) in enumerate(imgs):
            cv2.imwrite(f'textures/tone{i}-{x}.png', img)
        print("Finnish tone: ", target_tone)
