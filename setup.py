"""Setuptools entry point."""
import codecs
from setuptools import setup, find_packages
from os.path import join, dirname

tests_require = [
    'pytest==2.7.2',
    'pytest-cov==1.8.1',
    'pytest-cache==1.0',
    'pytest-django==2.8.0',
    'pytest-pythonpath==0.7'
]

descriptions = []

for filename in ('README.rst', 'CHANGES.rst', 'CONTRIBUTORS.rst'):
    with codecs.open(join(dirname(__file__), filename), encoding='utf-8') as fd:
        descriptions.append(fd.read())

setup(
    name='Arkestra',
    version='2.0.0',
    author='Daniele Procida',
    author_email='daniele@vurt.org',
    packages=find_packages(exclude=["example", "tests"]),  # exclude the example project
    include_package_data=True,
    zip_safe=False,
    license='LICENSE.txt',
    description='A semantic web publishing system for organisations',
    long_description="\n".join(descriptions),
    tests_require=tests_require,
    extras_require={'test': tests_require},
    install_requires=[
        'django >= 1.4, <=1.4.22',
        'easy-thumbnails==1.5',
        'django-typogrify',
        'BeautifulSoup',
        'django-cms==2.3.5',
        'django-filer==0.9.4',
        'semanticeditor',
        'pillow',
        'django-pagination',
        # 'django-easyfilters',
        'django-treeadmin',
        # 'django-widgetry',
        # 'django-chained-selectbox',
        'django-polymorphic==0.5.6',
        'html5lib==0.95',
    ],
)
