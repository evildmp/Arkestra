# register all interesting models for search

from arkestra_utilities.output_libraries.dates import nice_date
from news_and_events import models, admin
from news_and_events.templatetags.events_tags import event_date_and_time
from links import schema, LinkWrapper


class NewsWrapper(LinkWrapper):
    search_fields = admin.NewsArticleAdmin.search_fields
    heading = "Related news"

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
        """ % (status, date)

    def image(self):
        return self.obj.image

schema.register_wrapper([models.NewsArticle], NewsWrapper)


class EventWrapper(LinkWrapper):
    search_fields = admin.EventAdmin.search_fields
    heading = "Related events"

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

    def image(self):
        return self.obj.image

schema.register_wrapper([models.Event], EventWrapper)
