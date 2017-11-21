#! python3
import glob
import os
from PIL import Image


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


if __name__ == '__main__':
    from argparse import ArgumentParser
    from sample_transform import TRANSFORMS
    parser = ArgumentParser(
        'glitch_me',
        description='Adds some nice distortion/glitching to your images!'
    )
    parser.add_argument('input', help='Input image path glob pattern')
    parser.add_argument('output', help='Path to output directory')
    parser.add_argument('--line_count', type=int, help='The vertical resolution you want the glitches to operate at.')

    args = parser.parse_args()
    main(args.input, args.output, TRANSFORMS, line_count=args.line_count)
