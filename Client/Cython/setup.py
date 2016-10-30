from distutils.core import setup
from Cython.Build import cythonize

setup(
  name = 'CatanUtils',
  ext_modules = cythonize("CatanUtils.pyx"),
)