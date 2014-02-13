from .models import LinkType, ExternalLink

# from django.core.management.base import BaseCommand, NoArgsCommand, CommandError
# from django.contrib.contenttypes.models import ContentType
# 
# 
# from links.models import LinkType, ExternalLink
# 
# from optparse import make_option
# 
# class Command(BaseCommand):
# 
#     help = 'Reports and fixes links'
# 
#     def handle(self, **options):
#         self.stdout.write('Successfully ran command')
# 
#     def handle_noargs(self, **options):
#         self.stdout.write('Successfully ran command')
# 
# def duplicates():
#     # find out what link.kinds are permissible
#     permissible_kinds = LinkType.objects.all()
#     
#     # get the content_type of ExternalLinks
#     content_type = ContentType.objects.get_for_model(ExternalLink)
#     
#     print permissible_kinds, content_type
