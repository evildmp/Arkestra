from setuptools import setup, find_packages
from os.path import join, dirname

setup(
    name='Arkestra',
    version='2.0.0',
    author='Daniele Procida',
    author_email='daniele@vurt.org',
    packages=find_packages(exclude=["example"]), # exclude the example project
    include_package_data=True,
    zip_safe = False,
    license='LICENSE.txt',
    description='A semantic web publishing system for organisations',
    long_description=open(join(dirname(__file__), 'README.txt')).read(),
    install_requires=[
    'django==1.3.1',
    'django-typogrify', 
    'BeautifulSoup',
    'django-cms',
    'django-filer'
    'semanticeditor',
    'django-widgetry',  
    'pillow',
    ]
)
 
