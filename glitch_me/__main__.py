#! python3
"""
Add some glitch/distortion effects to images.

usage: glitch_me [-h] [-q] [--line_count LINE_COUNT] [-f FRAMES] [-d DURATION]
                 [-b]
                 {still,gif} input output_dir

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
"""
import glob
import os
from contextlib import ExitStack
from typing import Callable, Sequence

from PIL import Image, ImageOps, ImageStat
from tqdm import tqdm

from .effects import TransformationList
from .sample_transform import GIF_TRANSFORM, STATIC_TRANSFORM

ImageType = Image.Image


def apply_transformations(
    im: ImageType, funcs: TransformationList, progress_bar=None, file=None
) -> ImageType:
    """Take an Image and a list of functions and their args that return Images.

    Pass the output of the previous function into the next
    function. Return the output of the last function.

    im: a Pillow Image
    funcs: A list of 2-tuples where the first element is the function that
        takes a Pillow Image and returns a modified one, and the second element
        is a dictionary of the named args to be passed to that function in **
        notation.
    progress_bar: A tqdm progress bar that will be incremented by the size of
        the transformed image on every transformation.
    file: The name of the file being transformed, for printing with the
        progress bar.
    """
    transformed = im
    for func, args in funcs:
        if progress_bar:
            progress_bar.update(transformed.size[0] * transformed.size[1])
            progress_bar.set_description("{}: {}".format(file, func.__name__))
        transformed = func(transformed, **args)
    return transformed


def make_still(
    input_path: str,
    output_dir: str,
    transforms: TransformationList,
    line_count: int = None,
    progress_bar=None,
) -> Sequence[str]:
    """Make transformed image(s) from a list of functions.

    Select one or more image files from a glob pattern, apply a list of
    transforms to them, save the transformed images (with a `*_glitch.png`
    suffix) and return a list of their paths.

    input_path: A path to the image to be transformed.
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
    progress_bar: A tqdm progress bar.
    """
    if progress_bar:
        progress_bar.set_description("{}: Opening".format(input_path))
    im = Image.open(input_path)
    im = ImageOps.exif_transpose(im)

    # Handle initial image scaling
    original_size = im.size
    if line_count is not None:
        scale_factor = line_count / im.size[1]
        scaled_size = tuple(map(lambda val: int(val * scale_factor), im.size))
        im = im.resize(scaled_size, resample=Image.NEAREST)

    # Apply the transforms to the image
    output = apply_transformations(im, transforms, progress_bar, input_path)

    # Reverse the initial image scaling
    if line_count is not None:
        output = output.resize(original_size, resample=Image.NEAREST)

    # Save the result and append the path to output_paths
    basename = os.path.basename(input_path)
    outname = "{}_glitch.png".format(os.path.splitext(basename)[0])
    out_path = os.path.join(output_dir, outname)
    if progress_bar:
        progress_bar.set_description("{}: Saving".format(out_path))
    output.save(out_path)
    im.close()

    return out_path


def make_gif(
    input_path: str,
    output_dir: str,
    transform_generator: Callable[[int, int], TransformationList],
    line_count: int,
    frames: int,
    duration: int,
    bounce: bool,
    progress_bar=None,
) -> Sequence[str]:
    """Make transformed gif(s) from a list of functions.

    Select one or more image files from a glob pattern, apply a list of
    transforms to them using a progressive parameter to create a frame
    animation, save the transformed images (with a `*_glitch.gif` suffix) and
    return a list of their paths.

    input_path: A path to the image to be transformed.
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
    progress_bar: A tqdm progress bar
    """
    if progress_bar:
        progress_bar.set_description("{}: Opening".format(input_path))
    im = Image.open(input_path)
    im = ImageOps.exif_transpose(im)

    # Handle initial image scaling
    original_size = im.size
    if line_count is not None:
        scale_factor = line_count / im.size[1]
        scaled_size = tuple(map(lambda val: int(val * scale_factor), im.size))
        im = im.resize(scaled_size, resample=Image.NEAREST)

    median_lum = ImageStat.Stat(im.convert("L")).median[0]
    frame_list = []
    for i in range(frames):
        # Create a list of transforms from the generator
        frame_transforms = transform_generator(i / frames, median_lum)
        # Apply those transforms to the image
        transformed_frame = apply_transformations(
            im, frame_transforms, progress_bar, input_path
        )
        # Reverse the initial image scaling
        if line_count is not None:
            transformed_frame = transformed_frame.resize(
                original_size, resample=Image.NEAREST
            )
        # Add the transformed image to the frame list
        frame_list.append(transformed_frame)

    if bounce:
        frame_list = frame_list + list(reversed(frame_list))[1:]

    # Save the result and append the path to output_paths
    basename = os.path.basename(input_path)
    outname = "{}_glitch.gif".format(os.path.splitext(basename)[0])
    out_path = os.path.join(output_dir, outname)

    # Call save() on the first frame, and add the rest in the args
    if progress_bar:
        progress_bar.set_description("{}: Saving".format(out_path))
    frame_list[0].save(
        out_path, save_all=True, append_images=frame_list[1:], duration=duration, loop=0
    )
    im.close()

    return out_path


def optional_progress_bar(quiet_flag: bool, *args, **kwargs) -> tqdm:
    """Conditionally return a tqdm progress par if `quiet_flag` is False."""
    if quiet_flag:
        return ExitStack()
    else:
        return tqdm(*args, **kwargs)


def main():
    """Run the CLI."""
    from argparse import ArgumentParser
    from sys import exit as sys_exit

    # region Parser Configuration # noqa: E265
    parser = ArgumentParser(
        "glitch_me", description="Add some glitch/distortion effects to images."
    )
    parser.add_argument(
        "mode",
        choices=["still", "gif"],
        help="Make a still glitched image, or a progressive glitch animation.",
    )
    parser.add_argument("input", help="Input image path glob pattern")
    parser.add_argument(
        "output_dir",
        help='Path to output directory  (files will be saved \
        with "_glitch" suffix)',
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        default=False,
        help="Include to not print the paths to the output image(s).",
    )
    parser.add_argument(
        "--line_count",
        type=int,
        help="The vertical resolution you want the glitches to operate at",
    )
    parser.add_argument(
        "-f",
        "--frames",
        type=int,
        default=20,
        help="The number of frames you want in your GIF (default: 20)",
    )
    parser.add_argument(
        "-d",
        "--duration",
        type=int,
        default=100,
        help="The delay between frames in ms (default: 100)",
    )
    parser.add_argument(
        "-b",
        "--bounce",
        action="store_true",
        default=False,
        help="Include if you want the gif to play backward to the beginning \
        before looping. Doubles frame count.",
    )
    # endregion # noqa: E265

    args = parser.parse_args()

    if not glob.glob(args.input):
        raise FileNotFoundError(
            'No files found that matched the input pattern "{}"'.format(args.input)
        )

    if args.mode == "still":
        # Calculate how much work needs to be done
        work = 0
        for input_path in glob.glob(args.input):
            im = Image.open(input_path)
            im = ImageOps.exif_transpose(im)
            size = (
                im.size[0] * im.size[1]
                if not args.line_count
                else int(
                    (im.size[0] * (args.line_count / im.size[1]))
                    * (im.size[1] * (args.line_count / im.size[1]))
                )
            )
            transform_count = len(STATIC_TRANSFORM)
            work += size * transform_count
            im.close()

        # Set up progress bar
        with optional_progress_bar(
            args.quiet,
            total=work,
            unit="px",
            unit_scale=True,
            unit_divisor=1000,
            leave=False,
        ) as pbar:
            # Loop over globbed files
            for input_path in glob.glob(args.input):
                out_path = make_still(
                    os.path.abspath(input_path),
                    os.path.abspath(args.output_dir),
                    STATIC_TRANSFORM,
                    line_count=args.line_count,
                    progress_bar=pbar if not args.quiet else None,
                )
                if not args.quiet:
                    pbar.clear()
                    print(out_path)
            pbar.close()

    elif args.mode == "gif":
        # Calculate how much work needs to be done
        work = 0
        for input_path in glob.glob(args.input):
            im = Image.open(input_path)
            im = ImageOps.exif_transpose(im)
            size = (
                im.size[0] * im.size[1]
                if not args.line_count
                else int(
                    (im.size[0] * (args.line_count / im.size[1]))
                    * (im.size[1] * (args.line_count / im.size[1]))
                )
            )
            # Assuming constant number of transforms per frame
            transform_count = len(GIF_TRANSFORM(0))
            num_frames = args.frames
            work += size * num_frames * transform_count
            im.close()

        # Set up progress bar
        with optional_progress_bar(
            args.quiet,
            total=work,
            unit="px",
            unit_scale=True,
            unit_divisor=1000,
            leave=False,
        ) as pbar:
            for input_path in glob.glob(args.input):
                out_path = make_gif(
                    os.path.abspath(input_path),
                    os.path.abspath(args.output_dir),
                    GIF_TRANSFORM,
                    line_count=args.line_count,
                    frames=args.frames,
                    duration=args.duration,
                    bounce=args.bounce,
                    progress_bar=pbar if not args.quiet else None,
                )
                if not args.quiet:
                    pbar.clear()
                    print(out_path)
            pbar.close()
    else:
        print('Mode "{mode}" not recognized.'.format(mode=args.mode))
        sys_exit(1)


if __name__ == "__main__":
    main()
