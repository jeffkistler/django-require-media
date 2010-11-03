from require_media.manager import RequirementManager
from require_media.conf import settings

class RequireMediaMiddleware(object):
    """
    Adds a dependency manager to the request for later use.
    """
    def process_request(self, request):
        manager = RequirementManager()
        setattr(request, settings.REQUEST_ATTR_NAME, manager)
        return None
