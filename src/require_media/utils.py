from os.path import splitext
from urlparse import urlparse

from django.core.urlresolvers import get_mod_func
from django.utils.importlib import import_module

from require_media.conf import settings

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

def get_manager(request):
    """
    Get the requirements manager from a request object.
    """
    return getattr(request, settings.REQUEST_ATTR_NAME)

def determine_requirement_group(requirement, groups):
    """
    Determine a group (type) for a requirement if possible.
    """
    result = urlparse(requirement)
    base, extension = splitext(result.path)
    extension = extension.replace(".", "")
    if extension in set(groups):
        return extension
    return None

def update_graph(graph, name, dependencies):
    """
    Add a node reference to a dependency graph.
    """
    if name not in graph:
        graph[name] = [0]
    for dependency in dependencies:
        graph[name].append(dependency)
        if dependency not in graph:
            graph[dependency] = [0]
        graph[dependency][0] = graph[dependency][0] + 1

def topological_sort(graph_dict):
    """
    Sort a graph in order of fewest children to most.

    The graph is represented by a dictionary mapping node identifiers to an
    info array of the form [num_incoming_arcs, <outgoing_arcs>...]

    See: http://www.logarithmic.net/pfh-files/blog/01208083168/sort.py
         http://www.bitformation.com/art/python_toposort.html
    """
    graph = graph_dict.copy()
    # First, we find the root nodes
    roots = [node for node, info in graph.items() if info[0] == 0]
    ordered = []
    # We then repeatedly emit a root node and remove it from the graph
    # Children will become roots through this process
    while len(roots) != 0:
        root = roots.pop()
        ordered.append(root)
        # Remove references from this root
        for child in graph[root][1:]:
            graph[child][0] = graph[child][0] - 1
            if graph[child][0] == 0:
                roots.append(child)
        del graph[root]
    # If there are nodes left, they must form a cycle
    if len(graph) != 0:
        return None
    return ordered
