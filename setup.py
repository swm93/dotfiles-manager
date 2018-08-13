import setuptools



setuptools.setup(
    name = 'dotfiles',
    version = '1.0.0',
    author = 'Scott Mielcarski',
    url = '',
    license = 'MIT',
    packages = ['dotfiles'],
    entry_points = {
        'console_scripts': [
            'dotfiles = dotfiles.__main__:main'
        ]
    },
    python_requires='>=3.7'
)