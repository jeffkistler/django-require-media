from django.core.urlresolvers import get_mod_func
from django.utils.importlib import import_module

def get_module_attribute(path):
    """
    Convert a string version of a function name to the callable object.
    """
    lookup_callable = None
    mod_name, attr = get_mod_func(path)
    mod = import_module(mod_name)
    if attr != '':
        lookup_callable = getattr(mod, attr)
    return lookup_callable
        
