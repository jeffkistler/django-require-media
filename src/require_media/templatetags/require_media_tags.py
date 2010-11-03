from django import template

from require_media.conf import settings
from require_media.renderers import get_renderer
from require_media.manager import determine_requirement_group

register = template.Library()

# Create a template variable for later use
request_var = template.Variable("request")

def get_manager(context):
    """
    Try and resolve the request variable in the given context and retrieve
    the requirement manager from it.
    """
    request = request_var.resolve(context)
    requirement_manager = getattr(request, settings.REQUEST_ATTR_NAME)
    return requirement_manager
#
# require_inline
#

class RequireInlineNode(template.Node):
    """
    Registers an inline media requirement with the requirement manager.
    """
    def __init__(self, requirement, nodelist, group=None, depends=None):
        self.requirement = requirement
        self.nodelist = nodelist
        self.group = group
        self.depends = depends or []
        self.request_var = template.Variable("request")

    def render(self, context):
        try:
            manager = get_manager(context)
            manager.add_inline(self.requirement, self.nodelist, self.group, self.depends)
        except (template.VariableDoesNotExist, AttributeError):
            pass
        return u""

def compile_require_inline_node(parser, token):
    """
    Register a required inline asset, such as CSS or JavaScript.

    There are two required arguments: ``name``, which is a name for the block,
    and ``group``, which is a type identifier for the block.

    All further arguments specify requirements the one being defined
    depends upon.

    A simple example::
    
        {% require_inline sidebar css %}

        #sidebar {
          color: #ff0;
        }

        {% end_require_inline %}

    """
    parts = token.split_contents()
    if not len(parts) >= 3:
        raise template.TemplateSyntaxError("%s tag requires two arguments: name and group" % parts[0])
    tag_name, requirement, group, depends = parts[0], parts[1], parts[2], parts[3:]
    nodelist = parser.parse(('end_require_inline',))
    parser.delete_first_token()
    requirement_aliases = settings.REQUIREMENT_ALIASES or {}
    group_aliases = settings.REQUIREMENT_GROUP_ALIASES or {}
    requirement = requirement_aliases.get(requirement) or requirement
    group = group_aliases.get(group) or group
    depends = [requirement_aliases.get(dependency, dependency) for dependency in depends]
    return RequireInlineNode(requirement, nodelist, group, depends)

register.tag("require_inline", compile_require_inline_node)

#
# require
#

class RequireNode(template.Node):
    """
    Registers an external media requirement with the requirement manager.
    """
    def __init__(self, requirement, group=None, depends=None):
        self.requirement = requirement
        self.group = group
        self.depends = depends or []
        self.request_var = template.Variable("request")

    def render(self, context):
        try:
            manager = get_manager(context)
            manager.add_external(self.requirement, self.group, self.depends)
        except (template.VariableDoesNotExist, AttributeError):
            pass
        return u""

def compile_require_node(parser, token):
    """
    Registers an external requirement with the current request context.
    
    The tag is invoked with the following signature::

        {% require [<group>] requirement [<depends> ...] %}

    The optional ``group`` argument specifies a requirement group, such as
    "css" or "js", the ``requirement`` argument specifies the desired
    requirement, and all further arguments are interpreted as requirements
    of the one currently being specified.

    A simple example that causes ``jquery.js`` to be added to the list of
    ``js`` requirements for the current request::

        {% require js jquery.js %}

    This more complicated example would add ``jquery-ui.js`` to the list of
    ``js`` requirements after ``jquery.js``::

        {% require js jquery-ui.js jquery.js %}

    """
    parts = token.split_contents()
    if not len(parts) >= 2:
        raise template.TemplateSyntaxError("%s tag requires one or more arguments" % parts[0])
    tag_name, args = parts[0], parts[1:]

    group_aliases = settings.REQUIREMENT_GROUP_ALIASES or {}
    requirement_aliases = settings.REQUIREMENT_ALIASES or {}
    potential_group = group_aliases.get(args[0]) or args[0]
    if potential_group and potential_group in settings.GROUPS:
        if not len(args) >= 2:
            raise template.TemplateSyntaxError("%s tag requires a requirement to be specified" % parts[0])
        group = potential_group
        args = args[1:]
    else:
        group = None
    requirement = requirement_aliases.get(args[0]) or args[0]
    depends = args[1:]
    depends = [requirement_aliases.get(dependency, dependency) for dependency in depends]
    if group is None:
        group = determine_requirement_group(requirement, settings.GROUPS)
    return RequireNode(requirement, group, depends)

register.tag("require", compile_require_node)


#
# render_requirements
#


# nodelist.render coerces node render output
# nodelist.render is called by:
#   blocknode
#   autoescapecontrolnode
#   filternode
#   fornode
#   spacelessnode
#   withnode

class DelayedRequirementsRenderer(object):
    """
    Delays requirement lookup until unicode coercion.
    """
    def __init__(self, manager, groups, context):
        self.manager = manager
        self.groups = groups
        self.groups_set = set(groups)
        self.context = context

    def __unicode__(self):
        parts = []
        ordered = self.manager.sort_requirements()
        ordered = filter(lambda requirement: requirement.group in self.groups_set, ordered)
        requirements = ordered
        requirements = []
        for group in self.groups:
            requirements.extend(filter(lambda requirement: requirement.group == group, ordered))
        for requirement in requirements:
            renderer = get_renderer(requirement.group)
            if renderer:
                parts.append(renderer.render(requirement, self.context))
        return u"".join(parts)


class RenderRequirementsNode(template.Node):
    """
    Renders registered requirements for a given group.

    NOTE: Should only be used in a base template to capture all
          declared requirements.
    """
    def __init__(self, groups=None):
        self.groups = groups
        self.request_var = template.Variable("request")

    def render(self, context):
        try:
            manager = get_manager(context)
            return DelayedRequirementsRenderer(manager, self.groups, context)
        except (template.VariableDoesNotExist, AttributeError), e:
            pass
        return u""


def compile_render_requirements_node(parser, token):
    """
    Renders required media assets for the current request context.

    Accepts an optional positional argument to specify the asset group
    to render.

    The following example renders all CSS assets::

        {% render_requirements css %}

    """
    args = token.split_contents()
    groups = args[1:] or settings.GROUPS
    return RenderRequirementsNode(groups)

register.tag("render_requirements", compile_render_requirements_node)
