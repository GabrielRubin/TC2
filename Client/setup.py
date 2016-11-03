#from distutils.core import setup
#from distutils.extension import Extension
#from Cython.Build import cythonize
#from Cython.Distutils import build_ext

# setup(
#   name = 'CatanUtils',
#   ext_modules = cythonize("CatanUtils.pyx"),
# )

from setuptools import setup
from setuptools import Extension
from Cython.Distutils import build_ext

module = 'CatanUtils'

ext_modules = [Extension(module, sources=[module + ".pyx"],
              include_dirs=['path1','path2'], # put include paths here
              library_dirs=[], # usually need your Windows SDK stuff here
              language='c++')]

setup(
    name = module,
    ext_modules = ext_modules,
    cmdclass = {'build_ext': build_ext},
    include_dirs = ['path1', 'path2']
)