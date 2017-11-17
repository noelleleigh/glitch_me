from PIL import ImageOps
import effects

_scaling_factor = 2

TRANSFORMS = [
    (effects.desample, {'factor': _scaling_factor}),
    (effects.split_color_channels, {'offset': 1}),
    (effects.sin_wave_distortion, {'mag': 3, 'freq': 1}),
    (effects.walk_distortion, {'max_step_length': 1}),
    (effects.shift_corruption, {'offset_mag': 2, 'coverage': 0.25}),
    (effects.convert, {'mode': 'RGB'}),
    (ImageOps.posterize, {'bits': 3}),
    # (ImageOps.solarize, {'threshold': 200}),
    (effects.sharpen, {'factor': 2.0}),
    (effects.upscale, {'factor': _scaling_factor}),
    (effects.add_transparent_pixel, {}),
]
