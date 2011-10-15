from django.contrib import admin
from django import forms

from filer.admin.videoadmin import VideoAdmin
from filer.models.videomodels import Video

from models import VideoVersion, ArkestraVideo


# class VideoVersionForm(forms.ModelForm):
#     class Meta:
#         model = VideoVersion


class VideoVersionInline(admin.TabularInline):
    # form = VideoVersionForm    
    model = VideoVersion
    readonly_fields = ('size', 'codec', 'status')
    extra = 0


class VideoVersionAdmin(admin.ModelAdmin):
    pass


class MyVideoAdmin(VideoAdmin):
    inlines = (VideoVersionInline,)

class ArkestraVideoAdmin(admin.ModelAdmin):
    inlines = (VideoVersionInline,)


admin.site.unregister(Video)
admin.site.register(Video, MyVideoAdmin)
admin.site.register(ArkestraVideo, ArkestraVideoAdmin)
admin.site.register(VideoVersion, VideoVersionAdmin)