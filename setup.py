from setuptools import setup, find_packages
from os.path import join, dirname

setup(
    name='Arkestra',
    version='2.0.0',
    author='Daniele Procida',
    author_email='daniele@vurt.org',
    packages=find_packages(exclude=["example"]),  # exclude the example project
    include_package_data=True,
    zip_safe=False,
    license='LICENSE.txt',
    description='A semantic web publishing system for organisations',
    long_description=open(join(dirname(__file__), 'README.txt')).read(),
    install_requires=[
        'django >= 1.4, <=1.4.10',
        'django-typogrify',
        'BeautifulSoup',
        'django-cms == 2.3.5',
        'django-filer',
        'semanticeditor',
        'pillow',
        'django-pagination',
        'django-easyfilters',
        'django-treeadmin',
        'django-widgetry',
        'django-chained-selectbox',
    ],
    dependency_links=[
        'https://github.com/evildmp/django-widgetry/archive/master.zip#egg=django-widgetry-0.9.2a1',
        'https://github.com/s-block/django-chained-selectbox.git@6658ef6acd041ea8beeba620b5aeba6057ddc8be#egg=django_chained_selectbox-dev',

    ],
)
