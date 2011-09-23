from django import forms
from cmsplugin_filer_video.models import FilerVideo

class VideoForm(forms.ModelForm):
    
    class Meta:
        model = FilerVideo
        exclude = ('page', 'position', 'placeholder', 'language', 'plugin_type')