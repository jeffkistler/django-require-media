from require_media.conf import settings

def require_media(request):
    """
    Adds the current requirements manager to context.
    """
    manager = getattr(request, settings.REQUEST_ATTR_NAME)
    return {
        settings.CONTEXT_VAR_NAME: manager,
    }
