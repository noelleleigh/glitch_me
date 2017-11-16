#! python3
import random
import math
from PIL import Image, ImageChops, ImageEnhance


def desample(im, factor):
    resized = im.resize(
        tuple(map(lambda val: int(val / factor), im.size)),
        resample=Image.NEAREST
    )
    return resized


def upscale(im, factor):
    resized = im.resize(
        tuple(map(lambda val: int(val * factor), im.size)),
        resample=Image.NEAREST
    )
    return resized


def crop(im, box):
    return im.crop(box)


def convert(im, mode):
    return im.convert(mode)


def split_channels(im, offset):
    bands = list(im.split())
    bands[0] = ImageChops.offset(bands[0], offset, 0)
    bands[2] = ImageChops.offset(bands[2], -offset, 0)
    merged = Image.merge(im.mode, bands)
    return merged


def sharpen(im, factor):
    sharpener = ImageEnhance.Sharpness(im)
    sharpened = sharpener.enhance(factor)
    return sharpened


def shift_corruption(im, offset_mag, ratio):
    corrupted = im
    for ypos in random.choices(range(0, im.size[1]), k=int(im.size[1] * ratio)):
        box = (0, ypos, corrupted.size[0], ypos + 1)
        line = corrupted.crop(box)
        offset = random.randint(-offset_mag, offset_mag)
        line = ImageChops.offset(line, offset, 0)
        corrupted.paste(line, box=box)
    return corrupted


def random_walk(length, max_step_length):
    output = []
    pos = 0
    for _ in range(length):
        pos += random.randint(-max_step_length, max_step_length)
        output.append(pos)
    return output


def walk_distortion(im, max_step_length):
    waved = im
    curve = random_walk(im.size[1], max_step_length)
    for ypos in range(im.size[1]):
        box = (0, ypos, waved.size[0], ypos + 1)
        line = waved.crop(box)
        offset = curve[ypos]
        line = ImageChops.offset(line, offset, 0)
        waved.paste(line, box=box)
    return waved


def wave_distortion(im, mag, freq):
    waved = im
    for ypos in range(im.size[1]):
        box = (0, ypos, waved.size[0], ypos + 1)
        line = waved.crop(box)
        offset = int(mag * math.sin((ypos / im.size[1]) * 2 * math.pi * freq))
        line = ImageChops.offset(line, offset, 0)
        waved.paste(line, box=box)
    return waved


def add_transparent_pixel(im):
    converted = im.convert(mode='RGBA')
    top_left_pixel_val = list(converted.getpixel((0, 0)))
    top_left_pixel_val[-1] = 254
    converted.putpixel((0, 0), tuple(top_left_pixel_val))
    return converted
