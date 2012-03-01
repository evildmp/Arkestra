from os.path import join
from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe

WYM_TOOLS = ",\n".join([
    "{'name': 'Italic', 'title': 'Emphasis', 'css': 'wym_tools_emphasis'}",
    "{'name': 'Bold', 'title': 'Strong', 'css': 'wym_tools_strong'}",
    "{'name': 'Superscript', 'title': 'Superscript', 'css': 'wym_tools_superscript'}",
    "{'name': 'Subscript', 'title': 'Subscript', 'css': 'wym_tools_subscript'}",
    "{'name': 'InsertOrderedList', 'title': 'Ordered_List', 'css': 'wym_tools_ordered_list'}",
    "{'name': 'InsertUnorderedList', 'title': 'Unordered_List', 'css': 'wym_tools_unordered_list'}",
    "{'name': 'Indent', 'title': 'Indent', 'css': 'wym_tools_indent'}",
    "{'name': 'Outdent', 'title': 'Outdent', 'css': 'wym_tools_outdent'}",
    "{'name': 'Undo', 'title': 'Undo', 'css': 'wym_tools_undo'}",
    "{'name': 'Redo', 'title': 'Redo', 'css': 'wym_tools_redo'}",
    "{'name': 'Paste', 'title': 'Paste_From_Word', 'css': 'wym_tools_paste'}",
    "{'name': 'ToggleHtml', 'title': 'HTML', 'css': 'wym_tools_html'}",
    #"{'name': 'CreateLink', 'title': 'Link', 'css': 'wym_tools_link'}",
    #"{'name': 'Unlink', 'title': 'Unlink', 'css': 'wym_tools_unlink'}",
    #"{'name': 'InsertImage', 'title': 'Image', 'css': 'wym_tools_image'}",
    #"{'name': 'InsertTable', 'title': 'Table', 'css': 'wym_tools_table'}",
    #"{'name': 'Preview', 'title': 'Preview', 'css': 'wym_tools_preview'}",
])

WYM_TOOLS = getattr(settings, "WYM_TOOLS", WYM_TOOLS)

WYM_CONTAINERS = ",\n".join([
    "{'name': 'P', 'title': 'Paragraph', 'css': 'wym_containers_p'}",
    "{'name': 'H1', 'title': 'Heading_1', 'css': 'wym_containers_h1'}",
    "{'name': 'H2', 'title': 'Heading_2', 'css': 'wym_containers_h2'}",
    "{'name': 'H3', 'title': 'Heading_3', 'css': 'wym_containers_h3'}",
    "{'name': 'H4', 'title': 'Heading_4', 'css': 'wym_containers_h4'}",
    "{'name': 'H5', 'title': 'Heading_5', 'css': 'wym_containers_h5'}",
    "{'name': 'H6', 'title': 'Heading_6', 'css': 'wym_containers_h6'}",
    "{'name': 'PRE', 'title': 'Preformatted', 'css': 'wym_containers_pre'}",
    "{'name': 'BLOCKQUOTE', 'title': 'Blockquote', 'css': 'wym_containers_blockquote'}",
    "{'name': 'TH', 'title': 'Table_Header', 'css': 'wym_containers_th'}",
])
    
WYM_CONTAINERS = getattr(settings, "WYM_CONTAINERS", WYM_CONTAINERS)

WYM_CLASSES = ",\n".join([
    "{'name': 'date', 'title': 'PARA: Date', 'expr': 'p'}",
    "{'name': 'hidden-note', 'title': 'PARA: Hidden note', 'expr': 'p[@class!=\"important\"]'}",
])
    
WYM_STYLES = ",\n".join([
    "{'name': '.hidden-note', 'css': 'color: #999; border: 2px solid #ccc;'}",
    "{'name': '.date', 'css': 'background-color: #ff9; border: 2px solid #ee9;'}",
])

WYM_CLASSES = getattr(settings, "WYM_CLASSES", WYM_CLASSES)
WYM_STYLES = getattr(settings, "WYM_STYLES", WYM_STYLES)

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
        