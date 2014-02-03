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
        'django-treeadmin'
    ]
)
