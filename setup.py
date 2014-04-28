from setuptools import setup

setup(
    name="ndb-x",
    version='0.0.1',
    description='Synchronization primitives for ndb tasklets on Google App Engine (GAE)',
    long_description=open('README.rst').read(),
    license='MIT',
    author='herr kaste',
    author_email='herr.kaste@gmail.com',
    url='https://github.com/kaste/ndb-x',
    platforms=['linux', 'osx', 'win32'],
    packages = ['ndbx'],
    zip_safe=False,
    classifiers=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: POSIX',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: MacOS :: MacOS X',
    'Topic :: Software Development :: Testing',
    'Topic :: Software Development :: Quality Assurance',
    'Topic :: Utilities',
    'Programming Language :: Python',
    ],
)