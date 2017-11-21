from PIL import ImageOps
import effects

TRANSFORMS = [
    (effects.convert, {'mode': 'RGB'}),
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
