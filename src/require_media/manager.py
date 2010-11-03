from os.path import splitext
from urlparse import urlparse


class Requirement(object):
    """
    Represents a required external static resource.
    """
    def __init__(self, requirement, group=None, depends=None):
        self.requirement = requirement
        self.group = group
        self.depends = depends or []

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
        result = urlparse(self.requirement)
        return bool(result.netloc)


class InlineRequirement(Requirement):
    """
    A static resource defined within a document.
    """
    def __init__(self, requirement, content, group=None, depends=None):
        self.content = content
        super(InlineRequirement, self).__init__(requirement, group, depends)

    def is_inline(self):
        return True


class RequirementManager(object):
    """
    A registry of static resources the response to a request may depend upon.
    """
    def __init__(self):
        self.requirements = []
        self.requirement_map = {}

    def add_external(self, requirement, group=None, depends=[]):
        """
        Register an external dependency with the manager.
        """
        node = Requirement(requirement, group, depends)
        self.requirements.append(node)
        self.requirement_map[requirement] = node

    def add_inline(self, requirement, content, group=None, depends=[]):
        """
        Register an inline dependency with the manager.
        """
        node = InlineRequirement(requirement, content, group, depends)
        self.requirements.append(node)
        self.requirement_map[requirement] = node

    def make_pairs(self, requirements):
        return make_pairs(requirements, self.requirement_map)

    def sort_requirements(self, groups=None):
        """
        Order the requirements in a given group in topological order.

        If no group given, return all requirements sorted in topological order.
        Items are returned in order their dependents require.
        """
        requirements = self.requirements
        pairs = self.make_pairs(requirements)
        ordered = sort_requirements(pairs)
        unique_originals = set(requirements)
        unique_ordered = set(ordered)
        non_requirements = list(unique_originals.difference(unique_ordered))
        result = ordered
        result.extend(non_requirements)
        if groups:
            # group_names = groups
            # if self.group_aliases:
            #     group_names.extend([to_name for from_name, to_name in filter(lambda from_name, to_name: to_name in group_names, result)])
            group_names = [self.group_aliases.get(name, name) for name in groups]
            result = filter(lambda requirement: requirement.group in group_names, result)
        return result

#
# Utilities
#

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

def make_pairs(requirements, requirement_map):
    """
    Make a list of parent, child requirement pairs.
    """
    pairs = []
    for requirement in requirements:
        depends = requirement.depends or []
        for parent in depends:
            pairs.append((requirement, requirement_map[parent]))
    return pairs

def sort_requirements(pairs):
    """
    Sort the requirements in topological order.
    """
    num_parents = {}
    children ={}
    for child, parent in pairs:
        if not parent in num_parents:
            num_parents[parent] = 0
        if not child in num_parents:
            num_parents[child] = 0
        num_parents[child] += 1
        children.setdefault(parent, []).append(child)

    result = [requirement for requirement in num_parents.keys() if num_parents[requirement] == 0]

    for parent in result:
        del num_parents[parent]
        if parent in children:
            for child in children[parent]:
                num_parents[child] -= 1
                if num_parents[child] == 0:
                    result.append(child)

    return result

