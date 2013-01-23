import os, subprocess

from posixpath import join, basename, splitext, exists

from django.core import urlresolvers
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.conf import settings

from cms.models import CMSPlugin

from filer.fields.file import FilerFileField
from filer.fields.image import FilerImageField
# from filer.fields.video import FilerVideoField
from filer.models.filemodels import File
from filer import settings as filer_settings


class Video(File):

    @classmethod
    def matches_file_type(cls, iname, ifile, request):
        # the extensions we'll recognise for this file type
        filename_extensions = ['.dv', '.mov', '.mp4', '.avi', '.wmv',]
        ext = os.path.splitext(iname)[1].lower()
        return ext in filename_extensions

    # we get to use Filer's video icon free
    _icon = "video"

    # def get_admin_url_path(self):
    #     return urlresolvers.reverse('admin:filer_video_change', args=(self.id,))


class ArkestraVideo(Video):
    class Meta:
        proxy = True
        verbose_name = "Video"


class FilerVideoField(FilerFileField):
    default_model_class = Video

class VideoPluginEditor(CMSPlugin):
    LEFT = "left"
    RIGHT = "right"
    FLOAT_CHOICES = ((LEFT, _("left")),
                     (RIGHT, _("right")),
                     )
    video = FilerVideoField()
    VIDEO_WIDTHS = (
        (1000.0, u"Automatic"),
        (u'Widths relative to the containing column', (
            (100.0, u"100%"),
            (75.0, u"75%"),
            (66.7, u"66%"),
            (50.0, u"50%"),
            (33.3, u"33%"),
            (25.0, u"25%"),
            )
        ),
        ('', u"Video's native width - on your head be it"),
    )
    width = models.FloatField(null=True, blank=True, choices = VIDEO_WIDTHS, default = 1000.0)

    use_description_as_caption = models.BooleanField(verbose_name = "Use description", default=False, help_text = "Use image's description field as caption")
    caption = models.TextField(_("Caption"), blank=True, null=True)
    float = models.CharField(_("float"), max_length=10, blank=True, null=True, choices=FLOAT_CHOICES)
    
    def __unicode__(self):
        if self.video:
            return self.video.label
        else:
            return u"Video %s" % self.caption
        return ''
        
class VideoVersion(models.Model):
    source = FilerVideoField()
    size = models.SmallIntegerField(blank=True, null=True,)
    codec = models.CharField(max_length=20, blank=True, null=True,)
    status = models.CharField(max_length=20, default = "newly-created", blank=True, null=True,)

    def codec_and_size(self):
        # returns a string containing codec and size - e.g. h264-720 - used in various ways, such as version filenames
        return "-".join((CODECS[self.codec]["code"], str(self.size)))

    def outputpath(self):
        # the output path and filename for the version
        return os.path.join(self.abs_directory_path(), \
        "-".join((self.filename_without_extension(), \
        self.codec_and_size())) \
        + CODECS[self.codec]["extension"])
        
    def filename_without_extension(self):
        # e.g. "video"
        return os.path.splitext(self.filename())[0].lower() 
        
    def abs_directory_path(self):
        # e.g. "/var/www/html/arkestra_medic/media/filer_private/2010/11/23/output"        
        return os.path.join(settings.MEDIA_ROOT, "rendered_video", self.directory())

    def filename(self):    
        # e.g. "video.dv"
        return os.path.basename(unicode(self.source.file)) 

    def directory(self):
        # e.g. "filer_private/2010/11/23"
        print ">> self                 ", self
        print ">> self.source          ", self.source
        print ">> self.source.file     ", self.source.file
        print ">> unicode(self.source.file)", unicode(self.source.file)
        print ">> os.path.dirname(unicode(self.source.file))", os.path.dirname(unicode(self.source.file)) 
        return os.path.dirname(unicode(self.source.file)) 

    def encode(self):
        print
        print "======== encoding video ========="
        print 
        # we're going to create an encoded version of our video
        # let's find out from the dictionaries what's required
        codec_profile = VERSIONS[self.codec][self.size]
        codec_code = CODECS[self.codec]["code"]
        encoder = codec_profile["encoder"]
        schema = ENCODERS[encoder]["schema"]
        command = [encoder]

        print "codec_profile", codec_profile
        print "codec_code", codec_code
        print "encoder", encoder
        print "schema", schema
        print "command", command
        
        # check the output folder exists; create it if not
        if not os.path.exists(self.abs_directory_path()):
            print ">>> the output folder doesn't exist:", self.abs_directory_path()
            os.makedirs(self.abs_directory_path())
            print ">>>that worked!"

        # loop over the schema and assemble the command
        for item in schema:
            # input and output are special cases, because they take values that aren't determined by the schema
            if item == "input":
                input_prefix = ENCODERS[encoder].get("input")
                if input_prefix:
                    command.append(input_prefix)
                command.append(self.source.file.path)
            elif item == "output":
                output_prefix = ENCODERS[encoder].get("output")
                if output_prefix:
                    command.append(output_prefix)
                command.append(self.outputpath())
            else:
                for option_prefix, option_value in codec_profile[item].items():
                    command.extend((option_prefix,str(option_value)))

        # immediately mark it as "encoding", so nothing else tries to encode it while we're doing this
        print ">>> mark as encoding"
        self.status = "encoding"
        self.save()
        
        # now do the encoding and don't let anything after this happen until we finish executing command:
        print ">>> saved status"
        print "command:", str(command)
        exit_status = subprocess.call(command) 
        print exit_status
        print ">>> exited from", command
        if exit_status == 0: # it's OK, so mark the version OK
            self.status = "ready"
            self.save()
            print ">>> saved OK"
        else:
            self.status = "failed" # mark it as failed because the command returned an error
            self.save()
            print ">>> save FAILED", exit_status

        # we should never return from here with the status still "encoding" - but that has happened - how?
        return self.status
       
    def url(self):
        # the url for a particular version
        return os.path.join(settings.MEDIA_URL, \
            "rendered_video", \
            self.directory(), \
            "-".join((self.filename_without_extension(),
            self.codec_and_size())) \
            + CODECS[self.codec]["extension"])

    def __unicode__(self):
        if self.source:
            return self.source.label
        else:
            return u"Video %s" % self.caption
        return ''

"""
We have a number of dictionaries to help describe what we're doing. Maybe they should be in settings, but they are here for now.

This could be made simpler, but it's more flexible this way - for example, this allows us to prefer one encoder for one size, and a different encoder for another - just in case.

ENCODERS provides infomration about the commands that will be used to perform the video re-encoding, in this format. Each item in ENCODERS is the commandline name of the program.

Each command has a different schema, because they get their input/output filenames in a different order and with different prefix.
"""
ENCODERS = {
        "HandBrakeCLI": {
            "schema": ("options", "input", "output"), # the order in which the program expects to receive its options
            "input": "--input",
            "output": "--output",
            },
        "ffmpeg2theora": {
            "schema": ("options", "output", "input"),   # the schema is quite different from the one above
            "output": "--output",
            # "input": "",
        },
    }

"""
CODECS contains information for the files that are created.

    'code' is a slugified version of the codec's name; it's added to the filename
    
    'description' and 'implications' are human-readable information
"""
CODECS = {
    "H.264": {
        "extension": ".mp4", 
        "code": "h264",
        "description": "MP4/H.264 format video",
        "implications": " - good support in Safari & iOS",
        },

    "Theora": {
        "extension": ".ogv", 
        "code": "theora",
        "description": "Ogg/Theora format video",
        "implications": " - good support in Firefox",
        },
    }

"""
SIZES is a tuple of the sizes we can encode to for output. It needs to be in order of increasing size.
"""

SIZES = (360,720)

"""
VERSIONS describes the different files we can encode to. 

Firstly, we list the different codecs we'll employ, then each size for each.

    'type' is the type attribute of the <source> element in HTML5
    'options' are what we pass to the command
"""

VERSIONS = {
    "H.264": {
        SIZES[0]:    {
                "encoder": "HandBrakeCLI",
                "type": 'video/mp4; codecs="avc1.42E01E, .mp4a.40.2"',  #supposedly, we should use the codecs attribute of the type attribute, but all it does for me is make Theora video stop working in Firefox
                "options": {
                    "--preset": "iPhone & iPod Touch", 
                    "--width": SIZES[0], #"--vb": "600",  
                    "--two-pass": "", 
                    "--turbo": "", 
                    "--optimize": "",
                    }, 
                },
        SIZES[1]:    {
                "encoder": "HandBrakeCLI",
                "type": 'video/mp4; codecs="avc1.42E01E, .mp4a.40.2"',
                "options": {
                    "--preset": "iPhone & iPod Touch", 
                    "--width": SIZES[1], #"--vb": "600",  
                    "--two-pass": "", 
                    "--turbo": "", 
                    "--optimize": "",
                    }, 
                },
            },
    "Theora": {
        SIZES[0]:   {
                "encoder": "ffmpeg2theora",
                "type": 'video/ogg; codecs="theora, vorbis"',
                "options": {
                    "--videoquality": "5", 
                    "--audioquality": "1", 
                    "--width": SIZES[0],
                    },
            },
        SIZES[1]:   {
                "encoder": "ffmpeg2theora",
                "type": 'video/ogg; codecs="theora, vorbis"',
                "options": {
                    "--videoquality": "5", 
                    "--audioquality": "1", 
                    "--width": SIZES[1],
                    },
            },
        },
    }

"""
We provide these so we know we which encoded videos are available or missing for each kind of player.
"""
PLAYERS = {
    "HTML5": ("H.264", "Theora"),
    "FLASH": ("H.264",),
    }                                    