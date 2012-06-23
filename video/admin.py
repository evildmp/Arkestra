from django.contrib import admin
# from django import forms
# 
# from django.utils.translation import ugettext  as _
# 
from filer.admin.fileadmin import FileAdmin
# 
from models import Video #, VideoVersion, ArkestraVideo
#                                                           

# class VideoVersionForm(forms.ModelForm):
#     class Meta:
#         model = VideoVersion


# class VideoAdminChangeForm(forms.ModelForm):
#     class Meta:
#         model = Video
# 
# class VideoAdmin(FileAdmin):
#     form = VideoAdminChangeForm
#     fieldsets = (
#         (None, {
#             'fields': ('name', 'owner','description')
#         }),
#         (None, {
#             'fields': ('is_public',)
#             
#         }),
#         (_('Advanced'), {
#             'fields': ('file','sha1',),
#             'classes': ('collapse',),
#         }),
#     )
#     
# 
admin.site.register(Video, FileAdmin)

# class VideoVersionInline(admin.TabularInline):
#     # form = VideoVersionForm    
#     model = VideoVersion
#     readonly_fields = ('size', 'codec', 'status')
#     extra = 0
# 
# 
# class VideoVersionAdmin(admin.ModelAdmin):
#     list_display = ('size', 'codec', 'status')
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
# admin.site.register(VideoVersion, VideoVersionAdmin)