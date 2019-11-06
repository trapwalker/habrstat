from setuptools import setup, find_packages


setup(
    name='habrstat',
    version='0.0.1',
    url='',
    license='mit',
    author='trapwalker',
    author_email='svpmailbox@gmail.com',
    description='Habr statistic scrambler',
    packages=find_packages(),
    keywords=['habr', 'stat',],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires='>=3.6',
    install_requires=[
        "click",
        "pathlib",
        "pyyaml",
        "charset_normalizer",
        "beautifulsoup4",
    ],
    entry_points={"console_scripts": 'habrstat=getdata:main'},
)
