from setuptools import setup, find_packages
from codecs import open
from os import path
from aspider import __version__

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# get the dependencies and installs
with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')

install_requires = [x.strip() for x in all_reqs if 'git+' not in x]
dependency_links = [x.strip().replace('git+', '')
                    for x in all_reqs if x.startswith('git+')]

setup(
    name='aspider',
    version=__version__,
    description='a spider using asyncio',
    long_description=long_description,
    url='https://github.com/gxtrobot/aspider',
    download_url='https://github.com/gxtrobot/aspider/tarball/' + __version__,
    license='BSD',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        "Programming Language :: Python :: 3.6",
    ],
    keywords='',
    packages=find_packages(exclude=['docs', 'tests*']),
    include_package_data=True,
    author='gxtrobot',
    python_requires=">=3.6",
    install_requires=["aiohttp", "requests_html"],
    dependency_links=dependency_links,
    author_email='gxtrobot@gmail.com',
    entry_points={"console_scripts": ["aspider = aspider.__main__:main"]},

)
