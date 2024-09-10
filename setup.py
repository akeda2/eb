from setuptools import setup, find_packages

setup(
    name='eb',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'altgraph',
        'packaging',
        'prompt_toolkit',
        'pyinstaller',
        'pyinstaller-hooks-contrib',
        'setuptools',
        'wcwidth',
    ],
    entry_points={
        'console_scripts': [
            'eb = eb.eb:main',
        ],
    },
    author='David Åkesson',
    url='https://github.com/akeda2/eb',
    description='EB - primitive line ebitor',
    long_description=open('README.md').read(),
    python_requires='>=3.7',
)