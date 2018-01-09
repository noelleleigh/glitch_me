#! python3
"""
Add some glitch/distortion effects to images.

usage: glitch_me [-h] [--line_count LINE_COUNT] [-f FRAMES] [-d DURATION] [-b]
                 {single,gif} input output_dir

positional arguments:
  {single,gif}          Make a single glitched image, or a progressive glitch
                        animation.
  input                 Input image path glob pattern
  output_dir            Path to output directory (files will be saved with
                        "_glitch" prefix)

optional arguments:
  -h, --help            show this help message and exit
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
"""
import glob
import os
from typing import Callable, Sequence
from PIL import Image, ImageStat
from effects import TransformationList

ImageType = Image.Image


def apply_transformations(
    im: ImageType, funcs: TransformationList
) -> ImageType:
    """Take an Image and a list of functions and their args that return Images.

    Pass the output of the previous function into the next
    function. Return the output of the last function.

    im: a Pillow Image
    funcs: A list of 2-tuples where the first element is the function that
        takes a Pillow Image and returns a modified one, and the second element
        is a dictionary of the named args to be passed to that function in **
        notation.
    """
    transformed = im
    for func, args in funcs:
        transformed = func(transformed, **args)
    return transformed


def make_still(input_pattern: str, output_dir: str,
               transforms: TransformationList,
               line_count: int=None) -> Sequence[str]:
    """Make transformed image(s) from a list of functions.

    Select one or more image files from a glob pattern, apply a list of
    transforms to them, save the transformed images (with a `*_glitch.png`
    suffix) and return a list of their paths.

    input_pattern: A glob pattern for choosing which files to transform
    output_dir: Path to the directory the resulting files should be stored in
    transforms: A list of 2-tuples where the first element is the function that
        takes a Pillow Image and returns a modified one, and the second element
        is a dictionary of the named args to be passed to that function in **
        notation.
    line_count: The effective vertical resolution of the transformed image. The
        transformations will be applied to an image that has been scaled
        to this vertical resolution, than scaled (nearest-neightbor) to its
        original resolution. Using a number smaller than the original vertical
        resolution will lead to a "pixelated" output image.
    """
    output_paths = []
    for input_path in glob.glob(input_pattern):
        im = Image.open(input_path)

        if line_count is not None:
            original_size = im.size
            scale_factor = line_count / im.size[1]
            scaled_size = tuple(
                map(lambda val: int(val * scale_factor), im.size)
            )
            im = im.resize(scaled_size, resample=Image.NEAREST)

        output = apply_transformations(im, transforms)

        if line_count is not None:
            output = output.resize(original_size, resample=Image.NEAREST)

        basename = os.path.basename(input_path)
        outname = '{}_glitch.png'.format(os.path.splitext(basename)[0])
        out_path = os.path.join(output_dir, outname)
        output_paths.append(out_path)
        output.save(out_path)

    return output_paths


def make_gif(input_pattern: str, output_dir: str,
             transform_generator: Callable[[int, int], TransformationList],
             line_count: int, frames: int, duration: int,
             bounce: bool) -> Sequence[str]:
    """Make transformed gif(s) from a list of functions.

    Select one or more image files from a glob pattern, apply a list of
    transforms to them using a progressive parameter to create a frame
    animation, save the transformed images (with a `*_glitch.gif` suffix) and
    return a list of their paths.

    input_pattern: A glob pattern for choosing which files to transform
    output_dir: Path to the directory the resulting files should be stored in
    transform_generator: A function that takes a `progress` argument
        (float 0 to 1) and a `median_lum` argument (int 0 to 255) and returns a
        list of 2-tuples where the first element is the function that takes a
        Pillow Image and returns a modified one, and the second element is a
        dictionary of the named args and their values to be passed to that
        function.
    line_count: The effective vertical resolution of the transformed image. The
        transformations will be applied to an image that has been scaled
        to this vertical resolution, than scaled (nearest-neightbor) to its
        original resolution. Using a number smaller than the original vertical
        resolution will lead to a "pixelated" output image.
    frames: The number of frames the animation will be spread across.
    duration: The duration of each frame in milliseconds.
    bounce: Whether to play the animation backwards after completion.
    """
    output_paths = []
    for input_path in glob.glob(input_pattern):
        im = Image.open(input_path)

        if line_count is not None:
            original_size = im.size
            scale_factor = line_count / im.size[1]
            scaled_size = tuple(
                map(lambda val: int(val * scale_factor), im.size)
            )
            im = im.resize(scaled_size, resample=Image.NEAREST)

        median_lum = ImageStat.Stat(im.convert('L')).median[0]
        frame_list = []
        for i in range(frames):
            frame_transforms = transform_generator(i / frames, median_lum)
            transformed_frame = apply_transformations(im, frame_transforms)
            if line_count is not None:
                transformed_frame = transformed_frame.resize(
                    original_size, resample=Image.NEAREST
                )
            frame_list.append(transformed_frame)

        if bounce:
            frame_list = frame_list + list(reversed(frame_list))[1:]

        basename = os.path.basename(input_path)
        outname = '{}_glitch.gif'.format(os.path.splitext(basename)[0])
        out_path = os.path.join(output_dir, outname)
        output_paths.append(out_path)
        frame_list[0].save(
            out_path,
            save_all=True,
            append_images=frame_list[1:],
            duration=duration,
            loop=0
        )

    return output_paths


if __name__ == '__main__':
    from argparse import ArgumentParser
    from sample_transform import STATIC_TRANSFORM, GIF_TRANSFORM
    parser = ArgumentParser(
        'glitch_me',
        description='Add some glitch/distortion effects to images.'
    )
    parser.add_argument(
        'mode', choices=['single', 'gif'],
        help='Make a single glitched image, or a progressive glitch animation.'
    )
    parser.add_argument('input', help='Input image path glob pattern')
    parser.add_argument(
        'output_dir', help='Path to output directory  (files will be saved \
        with "_glitch" prefix)'
    )
    parser.add_argument(
        '--line_count', type=int,
        help='The vertical resolution you want the glitches to operate at'
    )
    parser.add_argument(
        '-f', '--frames', type=int, default=20,
        help='The number of frames you want in your GIF (default: 20)'
    )
    parser.add_argument(
        '-d', '--duration', type=int, default=100,
        help='The delay between frames in ms (default: 100)'
    )
    parser.add_argument(
        '-b', '--bounce', action='store_true', default=False,
        help='Include if you want the gif to play backward to the beginning \
        before looping. Doubles frame count.'
    )

    args = parser.parse_args()
    if args.mode == 'single':
        make_still(
            args.input,
            args.output_dir,
            STATIC_TRANSFORM,
            line_count=args.line_count
        )
    elif args.mode == 'gif':
        make_gif(
            args.input,
            args.output_dir,
            GIF_TRANSFORM,
            line_count=args.line_count,
            frames=args.frames,
            duration=args.duration,
            bounce=args.bounce
        )
    else:
        print('Mode not recognized.')
