from django.contrib import admin
# from django import forms
# 
from django.utils.translation import ugettext  as _
# 
from filer.admin.fileadmin import FileAdmin
# 
from models import Video, VideoVersion
#                                                           

# class VideoVersionForm(forms.ModelForm):
#     class Meta:
#         model = VideoVersion


# class VideoAdminChangeForm(forms.ModelForm):
#     class Meta:
#         model = Video
# 

class VideoVersionInline(admin.TabularInline):
    # form = VideoVersionForm    
    model = VideoVersion
    readonly_fields = ('size', 'codec', 'status')
    extra = 0


class VideoAdmin(FileAdmin):
    inlines = (VideoVersionInline,)
    

admin.site.register(Video, VideoAdmin)


class VideoVersionAdmin(admin.ModelAdmin):
    list_display = ('size', 'codec', 'status')
# 
# 
# class MyVideoAdmin(VideoAdmin):
#     inlines = (VideoVersionInline,)
# 
# class ArkestraVideoAdmin(admin.ModelAdmin):
#     inlines = (VideoVersionInline,)
# 
# 
# admin.site.unregister(Video)
# admin.site.register(Video, MyVideoAdmin)
# admin.site.register(ArkestraVideo, ArkestraVideoAdmin)
admin.site.register(VideoVersion, VideoVersionAdmin)