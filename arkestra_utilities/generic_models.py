from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib.contenttypes.models import ContentType

from cms.models.fields import PlaceholderField

from filer.fields.image import FilerImageField

from arkestra_utilities.settings import (
    PLUGIN_HEADING_LEVELS, PLUGIN_HEADING_LEVEL_DEFAULT
    )
from arkestra_utilities.managers import ArkestraGenericModelManager
from arkestra_utilities.utilities import get_fallback_template

from links.models import ObjectLink

from contacts_and_people.models import Entity, Person


class ArkestraGenericModel(models.Model):
    class Meta:
        abstract = True

    objects = ArkestraGenericModelManager()

    # needs to be overriden in the sub-class with the appropriate string
    # for example: "contact-entity"
    # see link_to_more() below
    auto_page_view_name = ""

    # core fields
    title = models.CharField(
        max_length=255,
        help_text="e.g. Outrage as man bites dog in unprovoked attack"
        )
    short_title = models.CharField(
        max_length=255,  null=True, blank=True,
        help_text=u"e.g. Man bites dog (if blank, will be copied from Title)"
        )
    summary = models.TextField(
        verbose_name="Summary",
        null=False, blank=False,
        help_text="""
            e.g. Cardiff man arrested in latest wave of man-on-dog violence
            (maximum two lines)"""
        )
    published = models.BooleanField(
        default=False, verbose_name=_(u"Published"), db_index=True,
        help_text=_(u"Select when ready to be published")
        )
    in_lists = models.BooleanField(
        _(u"Listed"), default=True, db_index=True,
        help_text=_(u"If deselected, this item will not appear in lists")
        )
    body = PlaceholderField(
        'body', help_text="Not used or required for external items"
        )
    image = FilerImageField(on_delete=models.SET_NULL, null=True, blank=True)

    # universal plugin fields
    hosted_by = models.ForeignKey(
        Entity,
        on_delete=models.SET_DEFAULT,
        default=Entity.objects.default_entity_id(),
        related_name='%(class)s_hosted_events', null=True, blank=True,
        help_text=u"The entity responsible for publishing this item")
    publish_to = models.ManyToManyField(
        Entity, verbose_name="Also publish to",
        null=True, blank=True,
        related_name="%(class)s_publish_to",
        help_text=u"Use sensibly",
        )
    please_contact = models.ManyToManyField(
        Person,
        related_name='%(class)s_person',
        help_text=u"The person to whom enquiries should be directed",
        null=True, blank=True
        )
    IMPORTANCES = (
        (0, u"Normal"),
        (1, u"More important"),
        (10, u"Most important"),
        )
    importance = models.PositiveIntegerField(
        null=True, blank=False,
        default=0, choices=IMPORTANCES,
        help_text=u"Important items will be featured in lists")

    def __unicode__(self):
        return self.short_title or u''

    @property
    def has_expired(self):
        # the item is too old to appear in current lists, and should only be
        # listed in archives
        return False

    @property
    # if they are not being gathered together, mark them as important
    def get_importance(self):
        if self.importance:
            return "important"
        else:
            return ""

    @property
    def get_hosted_by(self):
        return self.hosted_by or Entity.objects.base_entity()

    # when looking at an instance of this model, we can ask for a link to
    # more of the same for the same entity
    def link_to_more(self):
        if self.get_hosted_by:
            return self.get_hosted_by.get_auto_page_url(
                self.auto_page_view_name
                )
        else:
            return ""

    @property
    def get_template(self):
        if self.get_hosted_by:
            return self.get_hosted_by.get_template()
        else:
            return get_fallback_template()

    @property
    def get_entity(self):
        """
        Real-world information, can be None
        """
        return self.hosted_by or \
            Entity.objects.get(id=Entity.objects.base_entity())

    @property
    def links(self):
        model = ContentType.objects.get_for_model(self)
        links = ObjectLink.objects.filter(
            content_type__pk=model.id,
            object_id=self.id).order_by('destination_content_type')
        return links

    @property
    def external_url(self):
        # if the inheriting model doesn't have an external_url attribute,
        # we'll give it a None one just in case this is needed
        return None

    @property
    def is_uninformative(self):
        if (
            self.external_url or self.body.cmsplugin_set.all()
            or self.please_contact.all() or self.links
            ):

            return False
        else:
            return True


class ArkestraGenericPluginOptions(models.Model):
    class Meta:
        abstract = True

    entity = models.ForeignKey(
        Entity,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text="Leave blank for autoselect",
        related_name="%(class)s_plugin")
    LAYOUTS = (
        ("sidebyside", u"Side-by-side"),
        ("stacked", u"Stacked"),
        )
    layout = models.CharField(
        "Plugin layout",
        max_length=25,
        choices=LAYOUTS, default="sidebyside"
        )
    FORMATS = (
        ("title", u"Title only"),
        ("details image", u"Details"),
        )
    format = models.CharField(
        "Item format", max_length=25, choices=FORMATS,
        default="details image"
        )
    heading_level = models.PositiveSmallIntegerField(
        choices=PLUGIN_HEADING_LEVELS,
        default=PLUGIN_HEADING_LEVEL_DEFAULT
        )
    ORDERING = (
        ("date", u"Date alone"),
        ("importance/date", u"Importance & date"),
        )
    order_by = models.CharField(
        max_length=25, choices=ORDERING, default="importance/date"
        )
    LIST_FORMATS = (
        ("vertical", u"Vertical"),
        ("horizontal", u"Horizontal"),
        )
    list_format = models.CharField(
        "List format", max_length=25,
        choices=LIST_FORMATS, default="vertical"
        )
    group_dates = models.BooleanField("Show date groups", default=True)
    limit_to = models.PositiveSmallIntegerField(
        "Maximum number of items",
        default=5, null=True, blank=True,
        help_text=u"Leave blank for no limit"
        )

    def sub_heading_level(self):
        # requires that we change 0 to None in the database
        if self.heading_level is None:
            # this means the user has chosen "No heading"
            # we need to give sub_heading_level a value
            return 6
        else:
            # so if headings are h3, sub-headings are h4
            return self.heading_level + 1


class ArkestraGenericPluginForm(object):
    def clean(self):
        super(ArkestraGenericPluginForm, self).clean()
        if "horizontal" in self.cleaned_data["list_format"]:
            self.cleaned_data["order_by"] = "importance/date"
            self.cleaned_data["format"] = "details image"
            self.cleaned_data["layout"] = "stacked"
            self.cleaned_data["group_dates"] = False
            if self.cleaned_data["limit_to"] > 3:
                self.cleaned_data["limit_to"] = 3
            if self.cleaned_data["limit_to"] < 2:
                self.cleaned_data["limit_to"] = 2
        # 0 is a silly number, and interferes with the way we calculate later
        if self.cleaned_data["limit_to"] == 0:
            self.cleaned_data["limit_to"] = None
        return self.cleaned_data


class ArkestraGenericPlugin(object):
    text_enabled = True
    admin_preview = False
    # default render_template - change it in your ArkestraGenericPlugin if
    # required
    render_template = "arkestra/generic_lister.html"

    def icon_src(self, instance):
        return "/static/plugin_icons/generic.png"
