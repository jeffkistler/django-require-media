from urlparse import urljoin

from django.conf import settings as project_settings
from require_media.conf import settings

MEDIA_URL = project_settings.MEDIA_URL


class RequirementRenderer(object):
    """
    A base class for rendering media requirements.
    """
    def build_url(self, requirement):
        """
        Build the URL for a given requirement.
        """
        if requirement.is_qualified_url():
            return requirement.requirement
        path = urljoin(MEDIA_URL, self.directory)
        return urljoin(path, requirement.requirement)

    def render(self, requirement, context):
        """
        Render a given requirement.
        """
        if requirement.is_inline():
            return self.render_inline(requirement, context)
        return self.render_external(requirement, context)

    def render_inline(self, requirement, context):
        """
        Internal method to render an inline requirement.
        """
        # render the nodelist
        content = requirement.content
        if hasattr(content, "render"):
            content = content.render(context) 
        return self.inline_template % content

    def render_external(self, requirement, context):
        """
        Internal method to render an external requirement.
        """
        url = self.build_url(requirement)
        return self.external_template % url


class JavaScriptRequirementRenderer(RequirementRenderer):
    directory = "js/"
    external_template = settings.JAVASCRIPT_EXTERNAL_TEMPLATE
    inline_template = settings.JAVASCRIPT_INLINE_TEMPLATE

# An instance of the JavaScript requirement renderer for convenience
javascript_requirement_renderer = JavaScriptRequirementRenderer()


class CSSRequirementRenderer(RequirementRenderer):
    directory = "css/"
    external_template = settings.CSS_EXTERNAL_TEMPLATE
    inline_template = settings.CSS_INLINE_TEMPLATE

# An instance of the CSS requirement renderer for convenience
css_requirement_renderer = CSSRequirementRenderer()


def get_renderer(group):
    """
    Get a renderer instance for the given group name.
    """
    from require_media.utils import get_module_attribute
    try:
        renderer_path = settings.RENDERERS[group]
        renderer = get_module_attribute(renderer_path)
        return renderer
    except (KeyError, ImportError, AttributeError):
        return None

