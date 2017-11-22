from PIL import Image, ImageOps
import effects

STATIC_TRANSFORM = [
    (effects.convert, {'mode': 'RGB'}),
    (effects.pixel_sort, {'mask_function': lambda val: 255 if val < 100 else 0}),
    (effects.split_color_channels, {'offset': 1}),
    (effects.swap_cells, {'rows': 20, 'cols': 20, 'swaps': 4}),
    (effects.add_noise_bands, {'count': 4, 'thickness': 10}),
    (effects.sin_wave_distortion, {'mag': 3, 'freq': 1}),
    (effects.walk_distortion, {'max_step_length': 1}),
    (effects.shift_corruption, {'offset_mag': 2, 'coverage': 0.25}),
    (ImageOps.posterize, {'bits': 3}),
    (effects.sharpen, {'factor': 2.0}),
    (effects.add_transparent_pixel, {}),
]


def GIF_TRANSFORM(progress, median_lum=128):
    return [
        (effects.convert, {'mode': 'RGB'}),
        (effects.pixel_sort, {
            'mask_function':
            lambda val, progress=progress, median_lum=median_lum:
                255 if val < median_lum * progress else 0
        }),
        (effects.sin_wave_distortion, {'mag': 10 * progress, 'freq': 2 * progress}),
        (effects.add_noise_bands, {'count': int(10 * progress), 'thickness': 10}),
        (effects.split_color_channels, {'offset': int(5 * progress)}),
        (effects.convert, {'mode': 'P', 'palette': Image.ADAPTIVE}),
    ]
