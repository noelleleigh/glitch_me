"""
Two sample transformation lists, one for static images, one generator for GIFs.

STATIC_TRANSFORM: List of 2-tuples:
    - Function: Image -> Image
    - dict: args passed to function

GIF_TRANSFORM: Function that returns a list in the form of STATIC_TRANSFORM
"""
from math import pi, cos
from PIL import Image, ImageOps
from . import effects


STATIC_TRANSFORM = [
    (effects.convert, {'mode': 'RGB'}),
    (effects.pixel_sort, {
        'mask_function': lambda val: 255 if val < 100 else 0
    }),
    (effects.split_color_channels, {'offset': 1}),
    (effects.add_noise_bands, {'count': 4, 'thickness': 10}),
    (effects.sin_wave_distortion, {'mag': 3, 'freq': 1}),
    (effects.walk_distortion, {'max_step_length': 1}),
    (effects.shift_corruption, {'offset_mag': 2, 'coverage': 0.25}),
    (effects.low_res_blocks, {
        'rows': 15, 'cols': 15, 'cells': 4, 'factor': 2
    }),
    (effects.sharpen, {'factor': 2.0}),
    (effects.add_transparent_pixel, {}),
]


def GIF_TRANSFORM(
    progress: float, median_lum: int=128
) -> effects.TransformationList:
    """Return a list functions and arguments for a given `progress`.

    Because this is intended for making GIFs, it also converts the image to RGB
    mode at the start, then Palette mode at the end.

    progress: A float from 0.0 to 1.0 that indicates how far into the frame
        animation we are.
    median_lum: The median luminance of the image (integer from 0 to 255),
        useful for controlling pixel sorting.
    """
    loop_progress = -cos(2*pi*progress)/2 + 0.5
    lum_limit = median_lum + 0.5 * median_lum
    lum_limit = lum_limit if lum_limit <= 255 else 255

    return [
        (effects.convert, {'mode': 'RGB'}),
        (effects.pixel_sort, {
            'mask_function':
            lambda val, factor=loop_progress, limit=lum_limit:
                255 if val < limit * factor else 0,
            'reverse': True
        }),
        (effects.sin_wave_distortion, {
            'mag': 5, 'freq': 1, 'phase': -2*pi*progress
        }),
        (effects.add_noise_bands, {
            'count': int(10 * loop_progress), 'thickness': 10
        }),
        (effects.low_res_blocks, {
            'rows': 10, 'cols': 10, 'cells': int(10 * progress), 'factor': 4
        }),
        (ImageOps.posterize, {'bits': int(5 * (1 - loop_progress) + 3)}),
        (effects.split_color_channels, {'offset': int(5 * loop_progress)}),
        (effects.convert, {'mode': 'P', 'palette': Image.ADAPTIVE}),
    ]
