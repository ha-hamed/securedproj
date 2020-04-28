from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory, TestCase
from webapp import models

from .views import CreateSecuredResource


class SecuredResourceTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="test", email="test@…", password="top_secret")

    def test_get_anonymous_user(self):

        req = RequestFactory().get("/")
        req.user = AnonymousUser()
        resp = CreateSecuredResource.as_view()(req, *[], **{})
        self.assertEqual(resp.status_code, 302)

    def test_get_loggedin_user(self):

        req = RequestFactory().get("/")
        req.META["HTTP_USER_AGENT"] = "Chrome"
        req.user = models.User.objects.last()
        resp = CreateSecuredResource.as_view()(req, *[], **{})
        self.assertEqual(resp.status_code, 200)

    def test_post_Anonymous_user(self):

        req = RequestFactory().post("/")
        req.META["HTTP_USER_AGENT"] = "Chrome"
        req.user = AnonymousUser()

        req_kwargs = {"res_type": 1,
                      "url": "http://google.com", "res_file": ""}

        resp = CreateSecuredResource.as_view()(req, *[], **req_kwargs)
        self.assertEqual(resp.status_code, 302)

    def test_post_loggedin_user(self):

        req = RequestFactory().post("/")
        req.META["HTTP_USER_AGENT"] = "Chrome"
        req.user = models.User.objects.last()

        req_kwargs = {"res_type": 1,
                      "url": "http://google.com", "res_file": ""}

        resp = CreateSecuredResource.as_view()(req, *[], **req_kwargs)
        self.assertEqual(resp.status_code, 200)
