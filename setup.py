from setuptools import setup, find_packages

setup(
    name='Arkestra',
    version='2.0.0',
    author='Daniele Procida',
    author_email='daniele@vurt.org',
    packages=find_packages(),
    # packages=(
    #     'arkestra_utilities',
    #     'arkestra_image_plugin',
    #     'contacts_and_people',
    #     'housekeeping',
    #     'links',
    #     'news_and_events',
    #     'vacancies_and_studentships',
    #     # 'video',
    ),
    license='LICENSE.txt',
    description='A semantic web publishing system for organisations',
    long_description=open(join(dirname(__file__), 'README.txt')).read(),
    # requires=[
    #     "Django==1.3.1",            # Django, obviously
    #     "django-cms==2.2",          # and django CMS
    #     "South==0.7.5",             # for migrations
    #     "django-mptt==0.5.1",       # necessary to force the right version
    #     "django-typogrify==1.3",    # for HTML typography
    #     "django-polymorphic",       # not sure what needs this
    #     "django-appmedia",
    #     
    #     # for the semantic editor
    #     "pyquery==1.1.1",
    #     "lxml==2.3.4",
    #     "ElementTree",
    #     
    #     "BeautifulSoup==3.2.1",     # for the template introsepction
    #     
    #     # for images
    #     "PIL==1.1.7",               # never works properly 
    #     "easy-thumbnails==1.0-alpha-21", # hooray for SmileyChris
    # ],
)
 
"""
$ pip freeze
BeautifulSoup==3.2.1
Django==1.3.1
PIL==1.1.7
South==0.7.5
cssselect==0.7.1
django-appmedia==1.0.1
django-classy-tags==0.3.4.1
django-cms==2.2
django-mptt==0.5.1
django-polymorphic==0.2
django-sekizai==0.6.1
django-typogrify==1.3
easy-thumbnails==1.0-alpha-21
elementtree==1.2.7-20070827-preview
html5lib==0.95
lxml==2.3.4
pyquery==1.2.1
smartypants==1.6.0.3
wsgiref==0.1.2
"""   