#-*- coding:utf-8 -*-

import setuptools
import grass

mod = grass
name = 'grass'

version = '0.1.0'

setuptools.setup(
    name=name,
    version=mod.__version__,
    modules=[name],
    install_requires=[
        ],
)
