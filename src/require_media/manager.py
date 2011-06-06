"""
Classes for managing requirements.
"""
from urlparse import urlparse

from require_media.utils import update_graph, topological_sort

class Requirement(object):
    """
    Represents a required static resource.
    """
    def __init__(self, name, group=None, depends_on=None):
        self.name = name
        self.group = group
        self.depends_on = depends_on or []

    def is_inline(self):
        """
        Is this requirement an inline block?
        """
        return False

    def is_qualified_url(self):
        """
        Is the requirement a fully qualified URL?
        """
        if self.is_inline():
            return False
        result = urlparse(self.name)
        return bool(result.netloc)

    def __str__(self):
        return self.name


class ExternalRequirement(Requirement):
    """
    A static resource linked to from a document.
    """
    pass


class InlineRequirement(Requirement):
    """
    A static resource defined within a document.
    """
    def __init__(self, name, content, group=None, depends_on=None):
        self.content = content
        super(InlineRequirement, self).__init__(name, group, depends_on)

    def is_inline(self):
        return True


class RequirementManager(object):
    """
    A registry of static resources the response to a request may depend upon.
    """
    def __init__(self):
        self.requirements = []
        self.requirements_map = {}
        self.graph = {}
        self.sorted = None

    def add_external(self, name, group=None, depends_on=None):
        """
        Register an external (linked) requirement with the manager.
        """
        node = ExternalRequirement(name, group, depends_on)
        self.add_node(node)
        
    def add_inline(self, name, content, group=None, depends_on=None):
        """
        Register an inline dependency with the manager.
        """
        node = InlineRequirement(name, content, group, depends_on)
        self.add_node(node)

    def add_node(self, node):
        """
        Update the registry.
        """
        # Clear the cache
        self.sorted = None
        self.requirements.append(node)
        self.requirements_map[node.name] = node
        # Update graph
        update_graph(self.graph, node.name, node.depends_on)

    def get_sorted_requirements(self):
        """
        Return the requirements in topological order.
        """
        if self.sorted is None:
            ordered = topological_sort(self.graph)
            if ordered:
                ordered = [self.requirements_map[name] for name in reversed(ordered)]
                self.sorted = ordered
            else:
                return self.requirements
        return self.sorted

    def get_sorted_requirements_for_groups(self, *groups):
        """
        Return the requirements for the given groups in topological order.
        """
        group_set = set(*groups)
        sorted_requirements = self.get_sorted_requirements()
        filtered = []
        for requirement in sorted_requirements:
            if requirement.group in group_set:
                filtered.append(requirement)
        return filtered
