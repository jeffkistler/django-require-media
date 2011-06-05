#: A mapping of group names to import paths to renderer instances
RENDERERS = {
    "js": "require_media.renderers.javascript_requirement_renderer",
    "css": "require_media.renderers.css_requirement_renderer"
}

#: The list of all recognized groups
GROUPS = ["css", "js"]

#: The name of the requirement attribute on the request object
REQUEST_ATTR_NAME = "_require_media_manager"

#: The name of the requirements manager in template context
CONTEXT_VAR_NAME = "requirements_manager"

#: The default template for external JavaScript requirements 
JAVASCRIPT_EXTERNAL_TEMPLATE = '<script src="%s"></script>'

#: The default template for inline JavaScript requirements
JAVASCRIPT_INLINE_TEMPLATE = '<script>%s</script>'

#: The default template for external CSS requirements
CSS_EXTERNAL_TEMPLATE = '<link rel="stylesheet" type="text/css" href="%s">'

#: The default template for inline CSS requirements
CSS_INLINE_TEMPLATE = '<style>%s</style>'

#: A mapping of requirement names to replacement names
REQUIREMENT_ALIASES = {}

#: A mapping of requirement group names to replacement names
REQUIREMENT_GROUP_ALIASES = {}
