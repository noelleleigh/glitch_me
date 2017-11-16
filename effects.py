#! python3
"""
Collection of pure functions for transforming and applying effects to Pillow
Images.
"""
import random
import math
from PIL import Image, ImageChops, ImageEnhance


def desample(im, factor):
    """Return an image scaled down by a given factor using nearest-neighbor
    resampling.

    im: Pillow Image to be downsampled
    factor: The factor by which the width and height of the image will be
    reduced. Example: image(24x15) -> desample factor 3 -> image(8x5)
    """
    resized = im.resize(
        tuple(map(lambda val: int(val / factor), im.size)),
        resample=Image.NEAREST
    )
    return resized


def upscale(im, factor):
    """Return an image scaled up by a given factor using nearest-neighbor
    resampling.

    im: Pillow Image to be upscaled
    factor: The factor by which the width and height of the image will be
    increased. Example: image(8x5) -> upscale factor 3 -> image(24x15)
    """
    resized = im.resize(
        tuple(map(lambda val: int(val * factor), im.size)),
        resample=Image.NEAREST
    )
    return resized


def crop(im, box):
    """Return an image cropped to the given bounding box.

    im: Pillow Image to be cropped
    box: 4-tuple of (left, upper, right, lower) positions for the crop
    """
    return im.crop(box)


def convert(im, mode):
    """Return an image converted to the given mode (e.g. "RGB", "CMYK", ...).

    See https://pillow.readthedocs.io/en/stable/handbook/concepts.html#modes for
    list of modes.

    im: Pillow Image to be converted
    mode: Image mode to be converted to
    """
    return im.convert(mode)


def split_color_channels(im, offset):
    """Return an image where the Red and Blue color channels are horizontally
    offset from the Green channel left and right respectively.

    im: Pillow Image
    offset: distance in pixels the color channels should be offset by
    """
    bands = list(im.split())
    bands[0] = ImageChops.offset(bands[0], offset, 0)
    bands[2] = ImageChops.offset(bands[2], -offset, 0)
    merged = Image.merge(im.mode, bands)
    return merged


def sharpen(im, factor):
    """Return an image that has been sharpened.

    im: Pillow Image
    factor: See https://pillow.readthedocs.io/en/stable/reference/ImageEnhance.html#PIL.ImageEnhance.Sharpness
    """
    sharpener = ImageEnhance.Sharpness(im)
    sharpened = sharpener.enhance(factor)
    return sharpened


def shift_corruption(im, offset_mag, coverage):
    """Return an image with some pixel rows randomly shifted left or right by a
    random amount, wrapping around to the opposite side of the image.

    im: Pillow Image
    offset_mag: The greatest magnitude (in pixels) the rows will be shifted by
    in either direction.
    coverage: The fraction of total rows that will be shifted by some amount (0.5 = half the rows will be shifted). Note: Because the possible range of
    shifts include zero, some rows may not be shifted even with a coverage of 1.
    """
    corrupted = im
    line_count = int(im.size[1] * coverage)
    for ypos in random.choices(range(0, im.size[1]), k=line_count):
        box = (0, ypos, corrupted.size[0], ypos + 1)
        line = corrupted.crop(box)
        offset = random.randint(-offset_mag, offset_mag)
        line = ImageChops.offset(line, offset, 0)
        corrupted.paste(line, box=box)
    return corrupted


def _random_walk(length, max_step_length):
    """Return a list of values that rise and fall randomly."""
    output = []
    pos = 0
    for _ in range(length):
        pos += random.randint(-max_step_length, max_step_length)
        output.append(pos)
    return output


def walk_distortion(im, max_step_length):
    """Return an image with rows shifted according to a 1D random-walk.

    im: Pillow Image
    max_step_length: The maximum step size (in pixels) that the random walk can take. Essentially, the permitted "abruptness" of the distortion
    """
    waved = im
    curve = _random_walk(im.size[1], max_step_length)
    for ypos in range(im.size[1]):
        box = (0, ypos, waved.size[0], ypos + 1)
        line = waved.crop(box)
        offset = curve[ypos]
        line = ImageChops.offset(line, offset, 0)
        waved.paste(line, box=box)
    return waved


def sin_wave_distortion(im, mag, freq):
    """Return an image with rows shifted according to a sine curve.

    im: Pillow Image
    mag: The magnitude of the sine wave
    freq: The frequency of the sine wave
    """
    waved = im
    for ypos in range(im.size[1]):
        box = (0, ypos, waved.size[0], ypos + 1)
        line = waved.crop(box)
        offset = int(mag * math.sin((ypos / im.size[1]) * 2 * math.pi * freq))
        line = ImageChops.offset(line, offset, 0)
        waved.paste(line, box=box)
    return waved


def add_transparent_pixel(im):
    """Return an image where the top-left pixel has a slight transparency to
    force Twitter to not compress it.

    im: Pillow Image
    """
    converted = im.convert(mode='RGBA')
    top_left_pixel_val = list(converted.getpixel((0, 0)))
    top_left_pixel_val[-1] = 254
    converted.putpixel((0, 0), tuple(top_left_pixel_val))
    return converted
