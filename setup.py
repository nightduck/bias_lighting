from distutils.core import setup, Extension
setup(name='bias_lighting', ext_modules=[ Extension('animations', sources=['animations.cpp']) ])