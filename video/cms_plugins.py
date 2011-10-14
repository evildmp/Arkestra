import os, models, bisect

from threading import Thread

from django.utils.translation import ugettext_lazy as _

from cms.plugin_pool import plugin_pool
from cms.plugin_base import CMSPluginBase

from arkestra_utilities.output_libraries.plugin_widths import *

from models import FilerVideoEditor, VideoVersion, CODECS, VERSIONS, SIZES, PLAYERS


class FilerVideoPluginPublisher(CMSPluginBase):
    model = FilerVideoEditor
    name = _("Video")
    render_template = "video/video.html"
    text_enabled = True
    admin_preview = False
    raw_id_fields = ('video',)
            
    def render(self, context, instance, placeholder):
        """
        Arkestra can calculate the exact pixel width of any column in any placeholder; however, this isn't available to all applications that might use the filer.
        
        So, we should make the calculations here optional, and for non-Arkestra implementations do something different
        """        
        instance.has_borders = False
                    
        # calculate the width of the placeholder
        placeholder_width = get_placeholder_width(context, instance)

        # widths a fraction of nominal container width (deprecated)
        if instance.width <= 10:
            width = placeholder_width/instance.width
     
        # widths relative to placeholder width
        else:
            # widths a percentage of placeholder width
            if instance.width <= 100:
                width = placeholder_width/100.0 * instance.width
                auto = False
        
            # automatic width      
            elif instance.width == 1000:
                width = placeholder_width
                auto = True
            
            # calculate the width of the block the image will be in
            width = calculate_container_width(context, instance, width, auto)
                   
        # shave off 5 point if the image is floated, to make room for a margin
        # see arkestra.css, span.image.left and span.image.right
        if instance.float:
            print "-5 for float"
            width = width - 5   
        
        if instance.use_description_as_caption:
            instance.caption = instance.caption or instance.image.description
        
        # given the width we want to show the video at, we have to find the most suitable (i.e. closest larger) video file version we have created
        index = bisect.bisect_left(SIZES,width)
        print "sizes", SIZES, width, index
        if index < len(SIZES): # not larger than the largest preset size?
            size = SIZES[index] # get the exact or closest larger size
        else:
            # choose the widest, if we don't have one wider
            size = SIZES[-1]

        # create the lists of missing and available items
        instance.missing_versions = []
        instance.available_versions = []

        # # get the video's status dictionary
        # version_status = instance.video.get_status()
        # print
        # print ">>> checking status of the video"
        
        for codec, codec_dictionary in CODECS.items():
            print "    checking...", codec, size
            version, created = VideoVersion.objects.get_or_create(source = instance.video, size = size, codec = codec)
            print version, version.status

            # get the version's codec_and_size identifier
            codec_and_size = version.codec_and_size()
            
            print codec_and_size
            
            # get the file path for the version
            videofilepath = version.outputpath()
            print "        Status:", version.status
            print "        Filepath:", videofilepath
        
            # does the file exist?
            if os.path.exists(videofilepath):
                print "        the file exists"
                # if it does, check that the status dictionary agrees

                if version.status == "ready":
                    print "        the file is there and marked as present"
                    # and add the version to available_versions
                    instance.available_versions.append(codec)
                else:
                    # # what if the status dictionary doesn't say that the file is ready?
                    instance.missing_versions.append(codec)
                    # if status check says it's encoding, leave it alone
                    if version.status == "encoding":
                        print "        but it must be still encoding"
                    else:
                        # if it's not "ready" and not "encoding", it must be "missing" or "failed"- so let's try to encode it
                        print "        but it's not marked as ready or encoding, so we'd better re-create it"
                        print "        videofilepath:", videofilepath
                        print "        codec:", version.codec

                        thread = Thread(target=version.encode, name=videofilepath)
                        print "        launching thread"
                        thread.start()
        
            # if the file doesn't exist
            else:
                print "        the file doesn't exist, so we need to create the missing version"
                print "        videofilepath:", videofilepath
                print "        codec:", version.codec

                thread = Thread(target=version.encode, name=videofilepath)
                print "        launching thread"
                thread.start()

        # now we need to list the versions available to the different players (HTML5 and Flash so far, but we could have others if we wanted). The same version (H.264) is currently used for both HTML5 and Flash
        instance.html5_formats = []
        instance.flash_formats = []
        # all_formats is a list of versions without any duplications
        instance.all_formats = []
        instance.available_versions = set(instance.available_versions)
        
        # let's assemble the list of versions available for HTML5
        instance.formats = {}
        print "available versions", instance.available_versions
        for player, player_codecs in PLAYERS.items():
            print "player", player, "player_codecs", player_codecs
            instance.formats[player] = []
            for codec in player_codecs:
                print "codec is", codec
                if codec in instance.available_versions:
                    print "adding", codec
                    # add all the information we'll need about this version to a dictionary
                    description = {"url": VideoVersion.objects.get(source = instance.video, codec = codec, size = size).url(), "type": VERSIONS[codec][size]["type"], "description": CODECS[codec]["description"], "implications": CODECS[codec]["implications"],}
                    instance.formats[player].append(description)
                    if description not in instance.all_formats:
                        instance.all_formats.append(description)
        
        instance.width = int(width)
        instance.height = int(width/1.5)
        context.update({
            'object':instance,
            #'link':instance.link, 
            #'image_url':instance.scaled_image_url,
            'width': int(width),
            'caption_width': int(width),
            'placeholder':placeholder,
        })
        print "returning from video plugin render"
        return context

plugin_pool.register_plugin(FilerVideoPluginPublisher)
