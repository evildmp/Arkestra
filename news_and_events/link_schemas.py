# register all interesting models for search

from arkestra_utilities.output_libraries.dates import nice_date
from news_and_events import models, admin
from news_and_events.templatetags.events_tags import event_date_and_time
from links import schema, LinkWrapper


class GenericWrapper(LinkWrapper):
    special_attributes = ["is_uninformative", "external_url"]

    def get_absolute_url(self):
        return self.obj.get_absolute_url()

    def image(self):
        return self.obj.image

    def is_uninformative(self):
        return self.obj.is_uninformative

    def external_url(self):
        return self.obj.external_url


class NewsWrapper(GenericWrapper):
    search_fields = admin.NewsArticleAdmin.search_fields
    heading = "Related news"
    block_level_item_template = "arkestra/generic_list_item.html"


    def date(self):
        return nice_date(self.obj.date)

    def admin_metadata(self):
        date = nice_date(self.obj.date)
        if self.obj.published:
            status = "<strong>Published:</strong>"
        else:
            status = """
                <span class='errornote'>Not published</span>
            """
        return """
        %s %s
        """ % (status, self.date())


schema.register_wrapper([models.NewsArticle], NewsWrapper)


class EventWrapper(GenericWrapper):
    search_fields = admin.EventAdmin.search_fields
    heading = "Related events"
    block_level_item_template = "news_and_events/event_list_item.html"

    special_attributes = [
        "parent",
        "show_parent_series",
        "calculated_summary",
        "get_dates",
        "get_times",
        "building",
        "is_uninformative",
        "informative_url",
         "external_url",
         ]

    link_format_choices = (
            ("title", u"Title only"),
            ("details", u"Title & summary"),
            ("details image", u"Title, summary & image"),
            ("programme image details", u"Programme item"),
        )

    def parent(self):
        return self.obj.parent

    def show_parent_series(self):
        return self.obj.show_parent_series

    def calculated_summary(self):
        return self.obj.calculated_summary

    def get_dates(self):
        return self.obj.get_dates()

    def get_times(self):
        return self.obj.get_times()

    def building(self):
        return self.obj.building

    def informative_url(self):
        return self.obj.informative_url

    def date(self):
        date_dict = event_date_and_time(context=None, event=self.obj)
        return ", ".join(date_dict["date_and_time"])

    def date_heading(self):
        date_dict = event_date_and_time(context=None, event=self.obj)
        return " & ".join(date_dict["date_and_time_heading"])

    def admin_metadata(self):
        date_heading = self.date_heading().capitalize()
        if self.obj.published and date_heading:
            status = "<strong>%s:</strong>" % date_heading
        elif self.obj.published:
            status = "<strong>Event series</strong>"
        else:
            status = """
                <span class='errornote'>Not published</span>
            """
        return """
        %s %s
        """ % (status, self.date())


schema.register_wrapper([models.Event], EventWrapper)
