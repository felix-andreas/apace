from setuptools import setup, find_packages

about = {}
with open('apace/__about__.py') as file:
    exec(file.read(), about)

with open('README.md') as file:
    readme = file.read()

setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    long_description=readme,
    long_description_content_type='text/markdown',
    url=about['__url__'],
    author=about['__author__'],
    license=about['__license__'],
    packages=find_packages(),
    package_data={
        'data': ['data'],
    },
    install_requires=['numpy', 'scipy', 'matplotlib', 'cffi>=1.0.0'],
    test_requires=['pytest'],
    setup_requires=['cffi>=1.0.0'],
    python_requires='>=3.6',
    cffi_modules=[
        "cffi_build/build_twiss_product.py:ffi_builder",
    ],
    entry_points={"console_scripts": ["apace = apace.cli:main"]},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Scientific/Engineering'
    ]
)
