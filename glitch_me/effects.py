#! python3
"""Collection of pure functions for transforming Pillow Images."""
import math
import random
from numbers import Real
from typing import Callable, Sequence, Tuple

from PIL import Image, ImageChops, ImageColor, ImageEnhance

ImageType = Image.Image
TransformationList = Sequence[Tuple[Callable[[ImageType], ImageType], dict]]


def desample(im: ImageType, factor: Real) -> ImageType:
    """
    Return an image scaled down by a factor using nearest-neighbor resampling.

    im: Pillow Image to be downsampled
    factor: The factor by which the width and height of the image will be
        reduced. Example: image(24x15) -> desample factor 3 -> image(8x5)
    """
    resized = im.resize(
        tuple(map(lambda val: int(val / factor), im.size)), resample=Image.NEAREST
    )
    return resized


def upscale(im: ImageType, factor: Real) -> ImageType:
    """
    Return an image scaled up by a factor using nearest-neighbor resampling.

    im: Pillow Image to be upscaled
    factor: The factor by which the width and height of the image will be
        increased. Example: image(8x5) -> upscale factor 3 -> image(24x15)
    """
    resized = im.resize(
        tuple(map(lambda val: int(val * factor), im.size)), resample=Image.NEAREST
    )
    return resized


def crop(im: ImageType, box: Tuple[int, int, int, int]) -> ImageType:
    """Return an image cropped to the given bounding box.

    im: Pillow Image to be cropped
    box: 4-tuple of (left, upper, right, lower) positions for the crop
    """
    return im.crop(box)


def convert(im: ImageType, **kwargs) -> ImageType:
    """Return an image converted to the given mode (e.g. "RGB", "CMYK", ...).

    See https://pillow.readthedocs.io/en/stable/handbook/concepts.html#modes
    for list of modes.

    See https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.convert
    for the arguments to Image.convert.

    im: Pillow Image to be converted
    kwargs: Keyword arguments passed to Image.convert
    """
    return im.convert(**kwargs)


def split_color_channels(im: ImageType, offset: int) -> ImageType:
    """
    Return an image where the color channels are horizontally offset.

    The Red and Blue color channels are horizontally offset from the Green
    channel left and right respectively.

    im: Pillow Image
    offset: distance in pixels the color channels should be offset by
    """
    bands = list(im.split())
    bands[0] = ImageChops.offset(bands[0], offset, 0)
    bands[2] = ImageChops.offset(bands[2], -offset, 0)
    merged = Image.merge(im.mode, bands)
    return merged


def sharpen(im: ImageType, factor: int) -> ImageType:
    """Return an image that has been sharpened.

    im: Pillow Image
    factor: See https://pillow.readthedocs.io/en/stable/reference/ImageEnhance.html#PIL.ImageEnhance.Sharpness
    """
    sharpener = ImageEnhance.Sharpness(im)
    sharpened = sharpener.enhance(factor)
    return sharpened


def shift_corruption(im: ImageType, offset_mag: int, coverage: float) -> ImageType:
    """Return an image with some rows randomly shifted left or right.

    Return an image with some pixel rows randomly shifted left or right by a
    random amount, wrapping around to the opposite side of the image.

    im: Pillow Image
    offset_mag: The greatest magnitude (in pixels) the rows will be shifted by
        in either direction.
    coverage: The fraction of total rows that will be shifted by some amount
        (0.5 = half the rows will be shifted). Note: Because the possible range
        of shifts include zero, some rows may not be shifted even with a
        coverage of 1.
    """
    corrupted = im
    line_count = int(im.size[1] * coverage)
    for ypos in random.choices(range(im.size[1]), k=line_count):
        box = (0, ypos, corrupted.size[0], ypos + 1)
        line = corrupted.crop(box)
        offset = random.randint(-offset_mag, offset_mag)
        line = ImageChops.offset(line, offset, 0)
        corrupted.paste(line, box=box)
    return corrupted


def _random_walk(length: int, max_step_length: int) -> Sequence[int]:
    """Return a list of values that rise and fall randomly."""
    output = []
    pos = 0
    for _ in range(length):
        pos += random.randint(-max_step_length, max_step_length)
        output.append(pos)
    return output


def walk_distortion(im: ImageType, max_step_length: int) -> ImageType:
    """Return an image with rows shifted according to a 1D random-walk.

    im: Pillow Image
    max_step_length: The maximum step size (in pixels) that the random walk can
        take. Essentially, the permitted "abruptness" of the distortion
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


def sin_wave_distortion(
    im: ImageType, mag: Real, freq: Real, phase: Real = 0
) -> ImageType:
    """Return an image with rows shifted according to a sine curve.

    im: Pillow Image
    mag: The magnitude of the sine wave
    freq: The frequency of the sine wave
    phase: The degree by which the cycle is offset (rads)
    """
    waved = im
    for ypos in range(im.size[1]):
        box = (0, ypos, waved.size[0], ypos + 1)
        line = waved.crop(box)
        offset = int(mag * math.sin(2 * math.pi * freq * (ypos / im.size[1]) + phase))
        line = ImageChops.offset(line, offset, 0)
        waved.paste(line, box=box)
    return waved


def add_transparent_pixel(im: ImageType) -> ImageType:
    """Return an image that won't be compressed by Twitter.

    Return an image where the top-left pixel has a slight transparency to
    force Twitter to not compress it.

    im: Pillow Image
    """
    converted = im.convert(mode="RGBA")
    top_left_pixel_val = list(converted.getpixel((0, 0)))
    top_left_pixel_val[-1] = 254
    converted.putpixel((0, 0), tuple(top_left_pixel_val))
    return converted


def _get_grid_boxes(im: ImageType, rows: int, cols: int) -> ImageType:
    """Return a list of 4-tuples for every box in a given grid of the image.

    im: Pillow image
    rows: Number of rows in the grid
    cols: Number of columns in the grid
    """
    cell_width = int(im.size[0] / cols)
    cell_height = int(im.size[1] / rows)

    grid_boxes = [
        (
            cell_x * cell_width,
            cell_y * cell_height,
            cell_x * cell_width + cell_width,
            cell_y * cell_height + cell_height,
        )
        for cell_y in range(rows)
        for cell_x in range(cols)
    ]
    return grid_boxes


def swap_cells(im: ImageType, rows: int, cols: int, swaps: int) -> ImageType:
    """Return an image which rectangular cells have swapped positions.

    im: Pillow Image
    rows: The number of rows in the grid
    cols: The number of columns in the grid
    swaps: the number of pairs of cells to swap
    """
    modified = im
    grid_boxes = _get_grid_boxes(modified, rows, cols)
    chosen_boxes = random.choices(grid_boxes, k=swaps * 2)
    box_pairs = [
        (chosen_boxes[2 * i], chosen_boxes[(2 * i) + 1])
        for i in range(int(len(chosen_boxes) / 2))
    ]
    for box1, box2 in box_pairs:
        cell1 = modified.crop(box1)
        cell2 = modified.crop(box2)
        modified.paste(cell1, box2)
        modified.paste(cell2, box1)
    return modified


def make_noise_data(length: int, min: int, max: int) -> Sequence[Tuple[int, int, int]]:
    """Return a list of RGB tuples of random greyscale values.

    length: The length of the list
    min: The lowest luminosity value (out of 100)
    max: The brightest luminosity value (out of 100)
    """
    return [
        ImageColor.getrgb("hsl(0, 0%, {}%)".format(random.randint(min, max)))
        for _ in range(length)
    ]


def add_noise_cells(im: ImageType, rows: int, cols: int, cells: int) -> ImageType:
    """Return an image with randomly placed cells of noise.

    im: Pillow Image
    rows: The number of rows in the cell grid
    cols: The number of columns in the cell grid
    cells: number of noise cells to be created
    """
    modified = im
    grid_boxes = _get_grid_boxes(modified, rows, cols)
    chosen_boxes = random.choices(grid_boxes, k=cells)
    for box in chosen_boxes:
        noise_cell = Image.new(modified.mode, (box[2] - box[0], box[3] - box[1]))
        noise_cell.putdata(
            make_noise_data(noise_cell.size[0] * noise_cell.size[1], 0, 75)
        )
        modified.paste(ImageChops.lighter(modified.crop(box), noise_cell), box)

    return modified


def add_noise_bands(im: ImageType, count: int, thickness: int) -> ImageType:
    """Return an image with randomly placed full-width bands of noise.

    im: Pillow Image
    count: The number of bands of noise
    thickness: Maximum thickness of the bands
    """
    modified = im.convert("RGBA")
    boxes = [
        (0, ypos, im.size[0], ypos + random.randint(1, thickness))
        for ypos in random.choices(range(im.size[1]), k=count)
    ]
    for box in boxes:
        noise_cell = Image.new(modified.mode, (box[2] - box[0], box[3] - box[1]))
        noise_cell.putdata(
            make_noise_data(noise_cell.size[0] * noise_cell.size[1], 0, 75)
        )
        combined_cell = ImageChops.lighter(modified.crop(box), noise_cell)
        combined_cell.putalpha(128)
        modified.alpha_composite(combined_cell, (box[0], box[1]))

    return modified.convert(im.mode)


def _get_lum(rgb: Tuple[int, int, int]) -> int:
    return int(0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2])


def _split_data(
    data: Sequence[Tuple[int, ...]], width: int
) -> Sequence[Sequence[Tuple[int, ...]]]:
    height = int(len(data) / width)
    return [data[(row * width) : (row * width + width)] for row in range(height)]


def pixel_sort(
    im: ImageType, mask_function: Callable[[int], int], reverse: bool = False
) -> ImageType:
    """Return a horizontally pixel-sorted Image based on the mask function.

    The default sorting direction is dark to light from left to right.

    Pixel-sorting algorithm from: http://satyarth.me/articles/pixel-sorting/

    im: Pillow Image
    mask_function: function that takes a pixel's luminance and returns
        255 or 0 depending on whether it should be sorted or not respectively.
    reverse: sort pixels in reverse order if True
    """
    # Create a black-and-white mask to determine which pixels will be sorted
    interval_mask = im.convert("L").point(mask_function)
    interval_mask_data = list(interval_mask.getdata())
    interval_mask_row_data = _split_data(interval_mask_data, im.size[0])

    # Go row by row, recording the starting and ending points of each
    # contiguous block of white pixels in the mask
    interval_boxes = []
    for row_index, row_data in enumerate(interval_mask_row_data):
        for pixel_index, pixel in enumerate(row_data):
            # This is the first pixel on the row and it is white -> start box
            if pixel_index == 0 and pixel == 255:
                start = (pixel_index, row_index)
                continue
            # The pixel is white and the previous pixel was black -> start box
            if pixel == 255 and row_data[pixel_index - 1] == 0:
                start = (pixel_index, row_index)
                continue
            # This is the last pixel in the row and it is white -> end box
            if pixel_index == len(row_data) - 1 and pixel == 255:
                end = (pixel_index, row_index + 1)
                interval_boxes.append((start[0], start[1], end[0], end[1]))
                continue
            # The pixel is (black) and (not the first in the row) and (the
            # previous pixel was white) -> end box
            if pixel == 0 and pixel_index > 0 and row_data[pixel_index - 1] == 255:
                end = (pixel_index, row_index + 1)
                interval_boxes.append((start[0], start[1], end[0], end[1]))
                continue

    modified = im
    for box in interval_boxes:
        # Take the pixels from each box
        cropped_interval = modified.crop(box)
        interval_data = list(cropped_interval.getdata())
        # sort them by luminance
        cropped_interval.putdata(sorted(interval_data, key=_get_lum, reverse=reverse))
        # and paste them back onto the image!
        modified.paste(cropped_interval, box=(box[0], box[1]))

    return modified


def low_res_blocks(
    im: ImageType, rows: int, cols: int, cells: int, factor: Real
) -> ImageType:
    """Return an image with randomly placed cells of low-resolution.

    im: Pillow Image
    rows: The number of rows in the cell grid
    cols: The number of columns in the cell grid
    cells: number of low-res cells to be created
    factor: the deresolution factor (factor 2: 8x8 -> 4x4)
    """
    modified = im
    grid_boxes = _get_grid_boxes(modified, rows, cols)
    chosen_boxes = random.choices(grid_boxes, k=cells)
    for box in chosen_boxes:
        low_res_cell = modified.crop(box)
        low_res_cell = low_res_cell.resize(
            tuple(map(lambda val: int(val / factor), low_res_cell.size)), Image.NEAREST
        )
        low_res_cell = low_res_cell.resize(
            tuple(map(lambda val: int(val * factor), low_res_cell.size)), Image.NEAREST
        )
        modified.paste(low_res_cell, (box[0], box[1]))

    return modified
