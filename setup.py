import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "NeuroUnits",
    version = "0.1",
    author = "Mike Hull",
    author_email = "mikehulluk@gmail.com",
    description = ("A library for parsing quantities and sets of equations involving units for computational neuroscience."),
    license = "BSD",
    url = "https://github.com/mikehulluk/NeuroUnits",

    package_dir = {'':'src' },
    packages=[ 'neurounits',
               'neurounits.ast',
               'neurounits.ast_builder',
               'neurounits.ast_builder.eqnsetbuilder_io',
               'neurounits.importers',
               'neurounits.importers.neuroml',
               'neurounits.unit_expr_parsing',
               'neurounits.unit_term_parsing',
               'neurounits.units_backends',
               'neurounits.visitors',
               'neurounits.visitors.bases',
               'neurounits.visitors.common',
               'neurounits.ast_annotations',
               'neurounits.visualisation',
               'neurounits.visualisation.mredoc',
               'neurounits.visualisation.networkx',
               'neurounits.codegen',
               'neurounits.codegen.cffi_functor',
               'neurounits.codegen.cpp',
               'neurounits.codegen.cpp.fixed_point',
               'neurounits.codegen.utils',
               'neurounits.codegen.utils.c_compilation',
               'neurounits.codegen.nmodl',
               'neurounits.codegen.python_functor',
               'neurounits.codegen.population_infrastructure',
               'neurounits.frontend.cmdline',
               'neurounits.frontend.gui',
               'neurounits.frontend',
               'neurounits.simulation_io',
               'neurounits.ast_operations',
               'neurounits.unit_data',
               'neurounitscontrib',
               'neurounitscontrib.demo',
               'neurounitscontrib.demo.plugins',
               'neurounitscontrib.test',
               'neurounitscontrib.test.plugins',
              ],
    # Could also have been done with 'scripts=':
    #entry_points = {
    #    'console_scripts': [
    #        'mreorg.curate = mreorg.curator.cmdline.mreorg_curate:main',
    #    ],
    #},

    #package_data={
    #    'mredoc':[
    #        'resources/*',
    #        'testing/*',
    #        'testing/test_data',
    #        ]
    #    },


    #data_files=[('mreorg/etc', ['etc/configspec.ini']),
    #            #('config', ['cfg/data.cfg']),
    #            #('/etc/init.d', ['init-script'])
    #            ],


    install_requires=['matplotlib','quantities', 'straight.plugin','networkx'],

    long_description=read('README.txt'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)



