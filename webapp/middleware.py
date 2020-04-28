import logging

# =======================================================
# User Agent of each registered user is updated
# for each and every request made to Django server
# =======================================================

# get an instance of a logger
logger = logging.getLogger(__name__)


class UserAgentUpdateMiddleware:

    # one time configuration and initialization
    def __init__(self, get_response):
        self.get_response = get_response

    # code to be executed for each request before the view (and later middleware) are called.
    def __call__(self, request):
        if (request.user.is_authenticated):

            http_user_agent = request.META["HTTP_USER_AGENT"]

            logger.info(
                f"updating user agent, user: {request.user},HTTP_USER_AGENT: {http_user_agent}")

            request.user.user_stat.last_user_agent = http_user_agent
            request.user.save()

        return self.get_response(request)
