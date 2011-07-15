from models import Insert
from django import forms
class InsertForm(forms.ModelForm):
    class Meta:
        model = Insert
        widgets = {'description': forms.Textarea(
              attrs={'cols':80, 'rows':5,},
            ),  
        }

from cms.admin.placeholderadmin import PlaceholderAdmin # if it's at the start of the file, it breaks imports somehow

from django.contrib import admin


class InsertAdmin(PlaceholderAdmin):
    pass
    
admin.site.register(Insert, InsertAdmin)
