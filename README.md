# glitch_me
![Screencap of a Shinto gate from the anime movie Your Name that has aesthetically pleasing visual distortions](readme_assets/gate_small_glitch.png)

Python module to add some distortion/glitch effects to images.

Inspired by the work of [DataErase](http://dataerase.tumblr.com/).

## Examples using the included transforms

(*Click images for larger view*)

| Original | Glitched | GIF'd |
|----------|----------|-------|
|![tokyo](readme_assets/tokyo_small.png) | ![tokyo glitched](readme_assets/tokyo_small_glitch.png) | ![tokyo glitched gif](readme_assets/tokyo_small_glitch.gif) |
|![cafe](readme_assets/cafe_small.png) | ![cafe glitched](readme_assets/cafe_small_glitch.png) | ![cafe glitched gif](readme_assets/cafe_small_glitch.gif) |
|![gate](readme_assets/gate_small.png) | ![gate glitched](readme_assets/gate_small_glitch.png) | ![gate glitched gif](readme_assets/gate_small_glitch.gif) |


## Dependencies
**Note:** This module may work with older versions of these, but compatibility is only guaranteed on these versions or newer.
- [Python 3.6](https://www.python.org/)
- [Pillow 5.x](https://pypi.python.org/pypi/Pillow/)
- [tqdm 4.x](https://pypi.python.org/pypi/tqdm)


## Install

### Download
```
git clone https://github.com/noelleleigh/glitch_me.git
```

### Recommended Install Method
Add the `glitch_me` to your Python scripts available on your path and automatically install dependencies by running:
```
pip install -e ./glitch_me
```

### No Install Method
If you don't want `glitch_me` added to your scripts, you can run it from within its folder with:
```
python -m glitch_me
```

## Usage

### Command Line Interface (CLI) Arguments
```
usage: glitch_me [-h] [-q] [--line_count LINE_COUNT] [-f FRAMES] [-d DURATION]
                 [-b]
                 {still,gif} input output_dir

Add some glitch/distortion effects to images.

positional arguments:
  {still,gif}           Make a still glitched image, or a progressive glitch
                        animation.
  input                 Input image path glob pattern
  output_dir            Path to output directory (files will be saved with
                        "_glitch" suffix)

optional arguments:
  -h, --help            show this help message and exit
  -q, --quiet           Include to not print the paths to the output image(s).
  --line_count LINE_COUNT
                        The vertical resolution you want the glitches to
                        operate at
  -f FRAMES, --frames FRAMES
                        The number of frames you want in your GIF (default:
                        20)
  -d DURATION, --duration DURATION
                        The delay between frames in ms (default: 100)
  -b, --bounce          Include if you want the gif to play backward to the
                        beginning before looping. Doubles frame count.
```
### Examples
Add glitch effects to a single image and save it to its existing directory:
```
glitch_me still /pictures/image.png /pictures
```

Add glitch effects to multiple images and save them to a different directory:
```
glitch_me still /pictures/*.png /pictures/glitched
```

Add glitch effects to a single image, pixelated to a vertical resolution of 200px:
```
glitch_me still --line_count 200 /pictures/image.png /pictures
```

Create a glitch GIF from a single image, pixelated to a vertical resolution of 200px, with 10 frames, 50ms frame delay:
```
glitch_me gif --line_count 200 -f 10 -d 50 /pictures/image.png /pictures
```

### Deeper Customization
The CLI was written as a thin shell and doesn't expose the many ways this library can modify an image. For fine-grained control over the actual transformations applied by the CLI, you must edit the file [`sample_transform.py`](glitch_me/sample_transform.py).

In [`sample_transform.py`](glitch_me/sample_transform.py), you'll find two important objects:

1. `STATIC_TRANSFORM`: A list of tuples, each containing a function reference and the arguments to pass into that function. This list of functions tells `glitch_me` how to transform your image.
2. `GIF_TRANSFORM`: A function that takes a value called `progress` that tells the function how far along it is in the animation. The function returns a list in the same format as `STATIC_TRANSFORM` that is used to transform a specific animation frame.

These two objects define what happens when you use the `still` or `gif` options in the CLI, respectively.

The functions referenced in both objects all have one thing in common: They take in a `Pillow.Image` object (and extra arguments) and return a `Pillow.Image` object (presumably modified from the input). If you look at the functions that are there already, you'll see that most of them come from the [`effects.py`](glitch_me/effects.py) file, where a lot of useful glitching functions are defined. You can use any function in there with the pattern `function_name(im: ImageType, ...) -> ImageType` to add a transformation.

#### Add a New Transformation Tutorial
Say you were looking through [`effects.py`](glitch_me/effects.py) and decided you wanted to add the effect `shift_corruption` to the GIF transformations.
1. First, check the function's *docstring* (the part under the `def ...` line surrounded by `"""`triple quotes`"""`) to learn what it does and how to use it.
2. `shift_corruption` takes three arguments:
    1. `im`: a Pillow Image (This one is handled by default in the function that uses `STATIC_TRANSFORM` and `GIF_TRANSFORM`)
    2. `offset_mag`: The furthest you want a pixel row to be shifted (in pixels)
    3. `coverage`: What percentage of rows will be shifted
3. Now that we know what the function needs, we need to decide what values to give it. The `GIF_TRANSFORM` function has a useful variable in it called `loop_progress`, which will let us make an effect that goes from clean, to glitchy, and back to clean over the course of the GIF animation. We'll do some math so that when `loop_progress` is 0.0, there's no glitching. When it's 1.0, there's maximum glitching. So if you want your maximum `offeset_mag` to be 10 pixels, then we would put `int(10 * loop_progress)` into that argument (the `int()` is to convert the floating point value to an integer, which is what that argument expects). The same principle applies for `coverage`.
4. So the code we'll be adding will look like:
    ```python
    (effects.shift_corruption, {
        'offset_mag': int(10 * loop_progress), 'coverage': 0.5 * loop_progress
    })
    ```
    (I've indented the arguments so the line isn't impractically long.)
5. Now we have to decide where in the multi-step transformation to add this line. Let's add it after the `sin_wave_distortion` (don't forget to add a comma to the end!), so the final list will look like:
    ```python
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
        (effects.shift_corruption, {
            'offset_mag': int(10 * loop_progress), 'coverage': 0.5 * loop_progress
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
    ```
6. Save your modified `sample_transform.py` try creating a GIF and admire your distorted, glitchy results!


