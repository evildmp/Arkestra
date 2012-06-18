from distutils.core import setup

setup(
    name='Arkestra',
    version='2.0.0',
    author='Daniele Procida',
    author_email='daniele@vurt.org',
    packages=(
        'contacts_and_people',
        'vacancies_and_studentships',
        'news_and_events',
        'links',
        'arkestra_utilities.widgets.combobox',
        'arkestra_image_plugin',
        # 'video',
        'housekeeping',
    ),
    url='http://pypi.python.org/pypi/Arkestra/',
    license='LICENSE.txt',
    description='A semantic web publishing system for organisations',
    long_description=open('README.txt').read(),
    install_requires=[
        "Django >= 1.3",
        "django-cms",
        "django-typogrify",
    ],
)
