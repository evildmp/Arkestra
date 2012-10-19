from os.path import join

from django import forms
from django.utils.safestring import mark_safe
from django.conf import settings

from arkestra_utilities.settings import WYM_TOOLS, WYM_CONTAINERS, WYM_CLASSES, WYM_STYLES


class WYMEditor(forms.Textarea):
    class Media:
        js = [join(settings.CMS_MEDIA_URL, path) for path in (
            'wymeditor/jquery.wymeditor.js',
            'wymeditor/plugins/resizable/jquery.wymeditor.resizable.js',
            'js/wymeditor.placeholdereditor.js',
            #'js/lib/ui.core.js',
            #'js/placeholder_editor_registry.js',
        )]
        """css = {
            'all': [join(settings.CMS_MEDIA_URL, path) for path in (
                        'css/jquery/cupertino/jquery-ui.css',
                    )],
        }"""

    def __init__(self, language=None, attrs=None):
        self.language = language or settings.LANGUAGE_CODE[:2]
        self.attrs = {'class': 'wymeditor'}
        if attrs:
            self.attrs.update(attrs)
        super(WYMEditor, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        rendered = super(WYMEditor, self).render(name, value, attrs)
        context = {
            'name': name,
            'language': self.language,
            'CMS_MEDIA_URL': settings.CMS_MEDIA_URL,
            'WYM_TOOLS': mark_safe(WYM_TOOLS),
            'WYM_CONTAINERS': mark_safe(WYM_CONTAINERS),
            'WYM_CLASSES': mark_safe(WYM_CLASSES),
            'WYM_STYLES': mark_safe(WYM_STYLES),
        }
        return rendered + mark_safe(u'''<script type="text/javascript">
            $(document).ready(function(){
                $('#id_%(name)s').wymeditor({
                    lang: '%(language)s',
                    skin: 'django',
                    skinPath: '%(CMS_MEDIA_URL)sjs/wymeditor/skins/django/',
                    updateSelector: '.submit-row input[type=submit]',
                    updateEvent: 'click',
                    logoHtml: '',
                    toolsItems: [
                        %(WYM_TOOLS)s
                    ],
                    containersItems: [
                            %(WYM_CONTAINERS)s
                        ],
                    classesItems: [
                            %(WYM_CLASSES)s
                        ],
                    editorStyles: [
                        %(WYM_STYLES)s
                        ],
                    
                });
            });
            </script>''' % context)
        