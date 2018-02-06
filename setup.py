"""Install script for glitch_me."""
from setuptools import setup

setup(
    name='glitch_me',
    version='1.0.0',
    description='Python module to add some distortion/glitch effects to images',
    # TODO: Add long_description
    url='https://github.com/noahleigh/glitch_me',
    author='Noah Leigh',
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
        'Pillow>=5',
        'tqdm>=4'
    ],
    python_requires='~=3.6',
    entry_points={
        'console_scripts': [
            'glitch_me=glitch_me.__main__:main',
        ],
    },
)
