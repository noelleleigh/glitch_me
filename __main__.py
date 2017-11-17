#! python3
import glob
import os
from PIL import Image


def apply_transformations(im, funcs):
    transformed = im
    for func, args in funcs:
        transformed = func(transformed, **args)
    return transformed


def main(input_pattern, output_dir, transforms):
    for input_path in glob.glob(input_pattern):
        im = Image.open(input_path)
        output = apply_transformations(im, transforms)
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

    args = parser.parse_args()
    main(args.input, args.output, TRANSFORMS)
