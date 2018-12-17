import os
from setuptools import setup

install_requires = [
    'simplejson>=3.5.3, < 4.0.0',
    'urllib3>=1.9, < 2.0.0',
    'lxml>=3.3.5, < 4.0.0',
    'pyyaml>=3.11, < 4.0.0',
]

try:
    import importlib
except ImportError:
    install_requires.append('importlib')

# Set the Readme as the long description
readme = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.md')

with open(readme) as f:
    long_description = f.read()

setup(
    name='libsolace',
    version='0.2.3',
    description='Solace Provisioning Helper using the Solace SEMP XML API',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Alexander Hermes',
    author_email='night_lynx@hotmail.com',
    url='https://github.com/ExalDraen/python-libsolace',
    packages=[
        'libsolace',
        'libsolace.data',
        'libsolace.plugins',
        'libsolace.items'
    ],
    keywords=['solace'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ],
    python_requires='>=2.7,<=3.0',
    package_data={'': ['*.xsd']},
    setup_requires=[
        'nose==1.3.3',
        'wheel',
        'simplejson'
    ],
    tests_require=[
        'unittest2==0.5.1',
        'coverage==3.7.1',
        'influxdb'
    ],
    install_requires=install_requires,
    scripts=[
        'bin/solace-provision.py'
    ]
)
