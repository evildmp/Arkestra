from os.path import join
from itertools import chain
from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe

class Combobox(forms.Select):
    class Media:
        js = [
            settings.CMS_MEDIA_URL + 'js/lib/jquery.js',
            settings.CMS_MEDIA_URL + 'js/lib/ui.core.js',
            settings.CMS_MEDIA_URL + 'js/placeholder_editor_registry.js',
            'combobox/ui.combobox.js',
            ]
        css = {'all': ['combobox/ui.combobox.css']}

    def __init__(self, attrs=None, choices=()):
        self.attrs = {'class': 'combobox'}
        if attrs:
            self.attrs.update(attrs)
        super(Combobox, self).__init__(attrs)

    def render(self, name, value, attrs=None, choices=()):
        option_values = []
        choices = list(choices)
        if not value in ['', None]:
            for option_value, option_label in chain(self.choices, choices):
                if isinstance(option_label, (list, tuple)):
                    for option_value2, option_label2 in option_label:
                        option_values.append(option_value2)
                else:
                    option_values.append(option_value)
            if not value in option_values:
                choices.append((value,value))
        rendered = super(Combobox, self).render(name, value, attrs, choices)
        context = {
            'name': name,
            'CMS_MEDIA_URL': settings.CMS_MEDIA_URL,
            'STATIC_URL': settings.STATIC_URL,
        }
        return rendered + mark_safe(u'''<script type="text/javascript">
            $(document).ready(function(){
                $('#id_%(name)s').combobox({autoShow: false,arrowURL:'%(STATIC_URL)scombobox/drop_down.png',});
            });
            </script>''' % context)

class ComboboxField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs.update({'widget': Combobox})
        return super(ComboboxField, self).__init__(*args, **kwargs)
    
    def clean(self, value):
        return super(ComboboxField, self).clean(value)
    
    def valid_value(self, value):
        "Check to see if the provided value is a valid choice"
        # all values are valid
        return True
