import os
import sys
from django.core import management

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "example.test_settings")

    management.call_command(
        'test',
        'arkestra_utilities',
        'contacts_and_people',
        'news_and_events',
        'vacancies_and_studentships',
        'links',
        # verbosity=2,
        )