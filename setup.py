"""Install script for glitch_me."""
from setuptools import setup
import os
readme_file = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'README.md'
)
try:
    from m2r import parse_from_file
    readme = parse_from_file(readme_file)
except ImportError:
    # m2r may not be installed in user environment
    with open(readme_file) as f:
        readme = f.read()

setup(
    name='glitch_me',
    version='2.0.0',
    description='Python module to add distortion/glitch effects to images',
    long_description=readme,
    url='https://github.com/noelleleigh/glitch_me',
    author='Noelle Leigh',
    classifiers=[
        'Intended Audience :: End Users/Desktop',
        'Topic :: Artistic Software',
        'Topic :: Multimedia :: Graphics :: Graphics Conversion',

        'License :: OSI Approved :: MIT License',

        'Natural Language :: English',

        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='glitch images art',
    py_modules=['glitch_me'],
    install_requires=[
        'Pillow>=7',
        'tqdm>=4'
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'glitch_me=glitch_me.__main__:main',
        ],
    },
)
