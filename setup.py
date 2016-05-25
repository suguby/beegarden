import os

from setuptools import setup


README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='beegarden',
    version='2.2.9',
    packages=['beegarden', ],
    include_package_data=True,
    license='BSD License',
    description='The package allows you to create Beegarden game for programmers.',
    long_description=README,
    url='https://github.com/suguby/beegarden',
    author='Shandrinov Vadim',
    author_email='suguby@gmail.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ],
    install_requires=[
        'robogame_engine==0.7.5',
    ]
)
