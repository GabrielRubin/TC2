#from distutils.core import setup
#from Cython.Build import cythonize
#
#setup(
#  name = 'CatanUtils',
#  ext_modules = cythonize("CatanUtils.pyx"),
#)
from Cython.Distutils import build_ext
from setuptools import setup
from setuptools import Extension

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