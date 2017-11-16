from PIL import ImageOps
import effects

_scaling_factor = 3

TRANSFORMS = [
    (effects.desample, {'factor': _scaling_factor}),
    (effects.split_channels, {'offset': 2}),
    (effects.wave_distortion, {'mag': 5, 'freq': 1}),
    (effects.walk_distortion, {'max_step_length': 1}),
    (effects.shift_corruption, {'offset_mag': 4, 'ratio': 0.25}),
    (ImageOps.posterize, {'bits': 3}),
    # (ImageOps.solarize, {'threshold': 200}),
    (effects.sharpen, {'factor': 2.0}),
    (effects.upscale, {'factor': _scaling_factor}),
    (effects.add_transparent_pixel, {}),
]
