#! python3
import glob
import os
from PIL import Image, ImageStat


def apply_transformations(im, funcs):
    transformed = im
    for func, args in funcs:
        transformed = func(transformed, **args)
    return transformed


def main(input_pattern, output_dir, transforms, line_count=None):
    for input_path in glob.glob(input_pattern):
        im = Image.open(input_path)

        if line_count is not None:
            original_size = im.size
            scale_factor = line_count / im.size[1]
            scaled_size = tuple(map(lambda val: int(val * scale_factor), im.size))
            im = im.resize(scaled_size, resample=Image.NEAREST)

        output = apply_transformations(im, transforms)

        if line_count is not None:
            output = output.resize(original_size, resample=Image.NEAREST)

        basename = os.path.basename(input_path)
        outname = '{}_glitch.png'.format(os.path.splitext(basename)[0])
        output.save(os.path.join(output_dir, outname))


def make_gif(input_pattern, output_dir, transform_generator, frames, duration, bounce):
    for input_path in glob.glob(input_pattern):
        im = Image.open(input_path)
        median_lum = ImageStat.Stat(im.convert('L')).median[0]
        frame_list = []
        for i in range(frames):
            i_transforms = transform_generator(i / frames, median_lum=median_lum*1.5)
            frame_list.append(apply_transformations(im, i_transforms))

        if bounce:
            frame_list = frame_list + list(reversed(frame_list))[1:]

        basename = os.path.basename(input_path)
        outname = '{}_anim.gif'.format(os.path.splitext(basename)[0])
        base_im = im.convert('RGB').convert('P', palette=Image.ADAPTIVE)
        frame_list[0].save(
            os.path.join(output_dir, outname),
            save_all=True,
            append_images=frame_list[1:],
            duration=duration,
            loop=0
        )


if __name__ == '__main__':
    from argparse import ArgumentParser
    from sample_transform import STATIC_TRANSFORM, GIF_TRANSFORM
    parser = ArgumentParser(
        'glitch_me',
        description='Adds some nice distortion/glitching to your images!'
    )
    parser.add_argument('mode', choices=['single', 'gif'], help='Make a single glitched image, or a progressive glitch animation.')
    parser.add_argument('input', help='Input image path glob pattern')
    parser.add_argument('output', help='Path to output directory')
    parser.add_argument('--line_count', type=int, help='The vertical resolution you want the glitches to operate at')
    parser.add_argument('-f', '--frames', type=int, default=10, help='The number of frames you want in your GIF (default: 10)')
    parser.add_argument('-d', '--duration', type=int, default=100, help='The delay between frames in ms (default: 100)')
    parser.add_argument('-b', '--bounce', action='store_true', default=False, help='Include if you want the gif to play backward to the beginning before looping. Doubles frame count (default: False)')

    args = parser.parse_args()
    if args.mode == 'single':
        main(
            args.input,
            args.output,
            STATIC_TRANSFORM,
            line_count=args.line_count
        )
    elif args.mode == 'gif':
        make_gif(
            args.input,
            args.output,
            GIF_TRANSFORM,
            frames=args.frames,
            duration=args.duration,
            bounce=args.bounce
        )
    else:
        print('Mode not recognized.')
