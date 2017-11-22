# glitch_me
Python module to add some distortion/glitch effects to images.

Inspired by the work of [DataErase](http://dataerase.tumblr.com/).

## Dependencies
- [Python 3](https://www.python.org/)
- [Pillow 4.x](https://pypi.python.org/pypi/Pillow/)

## tl; dr
```
git clone https://github.com/noahleigh/glitch_me.git
python ./glitch_me image_folder/*.png output_folder --line_count 120
```

## Usage
```
usage: glitch_me [-h] [--line_count LINE_COUNT] [-f FRAMES] [-d DURATION] [-b]
                 {single,gif} input output

Adds some nice distortion/glitching to your images!

positional arguments:
  {single,gif}          Make a single glitched image, or a progressive glitch
                        animation.
  input                 Input image path glob pattern
  output                Path to output directory

optional arguments:
  -h, --help            show this help message and exit
  --line_count LINE_COUNT
                        The vertical resolution you want the glitches to
                        operate at
  -f FRAMES, --frames FRAMES
                        The number of frames you want in your GIF (default:
                        10)
  -d DURATION, --duration DURATION
                        The delay between frames in ms (default: 100)
  -b, --bounce          Include if you want the gif to play backward to the
                        beginning before looping. Doubles frame count.
```

## Examples using the included transforms
| Original | Glitched | GIF'd |
|----------|----------|-------|
|![tokyo](readme_assets/tokyo_small.png) | ![tokyo glitched](readme_assets/tokyo_small_glitch.png) | ![tokyo glitched gif](readme_assets/tokyo_small_anim.gif) |
|![cafe](readme_assets/cafe_small.png) | ![cafe glitched](readme_assets/cafe_small_glitch.png) | ![cafe glitched gif](readme_assets/cafe_small_anim.gif) |
|![gate](readme_assets/gate_small.png) | ![gate glitched](readme_assets/gate_small_glitch.png) | ![gate glitched gif](readme_assets/gate_small_anim.gif) |
