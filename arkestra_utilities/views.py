from django.views.generic.base import View
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import Http404

from contacts_and_people.models import Entity

# a handy class-based view for lists of an Entity's items - news, events,
# clinical trials or whatever they might be
class ArkestraGenericView(View):
    # override the auto_page_attibute in sub-classes to check
    auto_page_attribute = None

    def get(self, request, *args, **kwargs):
        self.get_entity()

    def get_entity(self):
        slug = self.kwargs.get('slug', None)
        if slug:
            entity = get_object_or_404(Entity, slug=slug)
        else:
            entity = Entity.objects.base_entity()

        if not (entity.website and entity.website.published):
            raise Http404

        if self.auto_page_attribute and not getattr(
            entity, self.auto_page_attribute, None
        ):
            raise Http404

        self.entity = entity

    def response(self, request):
        request.auto_page_url = request.path
        # request.path = entity.get_website.get_absolute_url()
        # for the menu, so it knows where we are
        request.current_page = self.entity.get_website
        context = RequestContext(request)
        context.update({
            "entity": self.entity,
            "title": self.title,
            "meta": self.meta,
            "pagetitle": self.pagetitle,
            "generic_lister_template": self.generic_lister_template,

            # this will need to be dealt with!
            "intro_page_placeholder": self.entity.news_page_intro,

            'lister': self.lister,
            }
        )

        return render_to_response(
            "arkestra/entity_generic_lister_page.html",
            context,
        )
