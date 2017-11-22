#! python3
"""
Collection of pure functions for transforming and applying effects to Pillow
Images.
"""
import random
import math
from PIL import Image, ImageChops, ImageEnhance, ImageColor


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


def convert(im, **kwargs):
    """Return an image converted to the given mode (e.g. "RGB", "CMYK", ...).

    See https://pillow.readthedocs.io/en/stable/handbook/concepts.html#modes for
    list of modes.

    im: Pillow Image to be converted
    mode: Image mode to be converted to
    """
    return im.convert(**kwargs)


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
    for ypos in random.choices(range(im.size[1]), k=line_count):
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


def sin_wave_distortion(im, mag, freq, phase=0):
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


def _get_grid_boxes(im, rows, cols):
    """Return a list of 4-tuples for every bounding box in a given grid of
    the image.
    """
    cell_width = int(im.size[0] / cols)
    cell_height = int(im.size[1] / rows)

    grid_boxes = [
        (
            cell_x * cell_width,
            cell_y * cell_height,
            cell_x * cell_width + cell_width,
            cell_y * cell_height + cell_height
        )
        for cell_y in range(rows)
        for cell_x in range(cols)
    ]
    return grid_boxes


def swap_cells(im, rows, cols, swaps):
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
        (chosen_boxes[2*i], chosen_boxes[(2*i)+1])
        for i in range(int(len(chosen_boxes)/2))
    ]
    for box1, box2 in box_pairs:
        cell1 = modified.crop(box1)
        cell2 = modified.crop(box2)
        modified.paste(cell1, box2)
        modified.paste(cell2, box1)
    return modified


def make_noise_data(length, min, max):
    """Return a list of RGB tuples of random greyscale values

    length: The length of the list
    min: The lowest luminosity value (out of 100)
    max: The brightest luminosity value (out of 100)
    """
    return [
        ImageColor.getrgb('hsl(0, 0%, {}%)'.format(random.randint(min, max)))
        for _ in range(length)
    ]


def add_noise_cells(im, rows, cols, cells):
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
        noise_cell = Image.new(modified.mode, (box[2]-box[0], box[3]-box[1]))
        noise_cell.putdata(make_noise_data(noise_cell.size[0] * noise_cell.size[1], 0, 75))
        modified.paste(ImageChops.lighter(modified.crop(box), noise_cell), box)

    return modified


def add_noise_bands(im, count, thickness):
    """Return an image with randomly placed full-width bands of noise.

    im: Pillow Image
    count: The number of bands of noise
    thickness: Maximum thickness of the bands
    """
    modified = im.convert('RGBA')
    boxes = [
        (0, ypos, im.size[0], ypos + random.randint(1, thickness))
        for ypos in random.choices(range(im.size[1]), k=count)
    ]
    for box in boxes:
        noise_cell = Image.new(modified.mode, (box[2]-box[0], box[3]-box[1]))
        noise_cell.putdata(make_noise_data(noise_cell.size[0] * noise_cell.size[1], 0, 75))
        combined_cell = ImageChops.lighter(modified.crop(box), noise_cell)
        combined_cell.putalpha(128)
        modified.alpha_composite(combined_cell, (box[0], box[1]))

    return modified.convert(im.mode)


def _get_lum(rgb):
    return int(0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2])


def _split_data(data, width):
    height = int(len(data) / width)
    return [
        data[(row * width):(row * width + width)]
        for row in range(height)
    ]


def pixel_sort(im, mask_function, reverse=False):
    """Return an image that has been horizontally pixel sorted based on the
    mask function.

    im: Pillow Image
    mask_function: function that takes a pixel's luminance and decides if it will be sorted or not
    reverse: sort pixels in reverse order if True
    """
    interval_mask = im.convert('L').point(mask_function)
    interval_mask_data = list(interval_mask.getdata())
    interval_mask_row_data = _split_data(interval_mask_data, im.size[0])
    interval_boxes = []
    for row_index, row_data in enumerate(interval_mask_row_data):
        for pixel_index, pixel in enumerate(row_data):
            if pixel_index == 0 and pixel == 255:
                start = (pixel_index, row_index)
                continue
            if pixel == 255 and row_data[pixel_index - 1] == 0:
                start = (pixel_index, row_index)
                continue
            if pixel_index == len(row_data) - 1 and pixel == 255:
                end = (pixel_index, row_index + 1)
                interval_boxes.append((start[0], start[1], end[0], end[1]))
                continue
            if pixel == 0 and pixel_index > 0 and row_data[pixel_index - 1] == 255:
                end = (pixel_index, row_index + 1)
                interval_boxes.append((start[0], start[1], end[0], end[1]))
                continue

    modified = im
    for box in interval_boxes:
        cropped_interval = modified.crop(box)
        interval_data = list(cropped_interval.getdata())
        cropped_interval.putdata(sorted(interval_data, key=_get_lum, reverse=reverse))
        modified.paste(cropped_interval, box=(box[0], box[1]))

    return modified
