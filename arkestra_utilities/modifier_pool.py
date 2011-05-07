from django.conf import settings
from django.utils.importlib import import_module

class WidthAdjuster(object):
    def mark():
        return
    def modify():
        return

class AdjusterPool(object):
    def __init__(self):
        self.adjusters = {}
        self.discovered = False
    
    def discover_modifers(self):    
        if self.discovered:
            return    
        for app in settings.INSTALLED_APPS:
            try:
                import_module('.plugin_modifiers', app)
            except ImportError:
                pass
        from plugin_modifiers import register
        register()
        self.discovered = True

    def register_adjuster(self, modifier_class):
        print "registering", modifier_class
        assert issubclass(modifier_class, WidthAdjuster)
        # should we check if it's already registered?
        self.adjusters.setdefault(modifier_class.kind, []).append(modifier_class)

adjuster_pool = AdjusterPool()    
adjuster_pool.discover_modifers()