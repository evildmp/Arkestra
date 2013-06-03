from django.core.management.base import NoArgsCommand

# from links.models import ExternalLink, ObjectLink, GenericLinkListPluginItem, LinkType, ExternalSite


class ReportCommand(NoArgsCommand):
    help = "Reports on Arkestra links application"

    def handle_noargs(self, **options):
        """
        Obtains a report on links
        """
        self.stdout.write("Obtaining links report\n")
