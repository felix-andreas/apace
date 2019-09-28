from setuptools import setup, find_packages

about = {}
with open('elements/__about__.py') as file:
    exec(file.read(), about)

with open('README.md') as file:
    readme=file.read()

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
    install_requires=['numpy', 'matplotlib', 'cffi>=1.0.0'],
    setup_requires=['cffi>=1.0.0'],
    python_requires='>=3.6',
    cffi_modules=[
        "cffi_build/build_twiss_product.py:ffi_builder",
    ],
)
