from webapp import models
from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase, RequestFactory
from . import views

class SecuredResourceTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='test', email='test@…', password='top_secret')

    def test_get_anonymous_user(self):
        view_class = views.SecuredResourceCreate

        req = RequestFactory().get('/')
        req.user = AnonymousUser()
        resp = views.SecuredResourceCreate.as_view()(req, *[], **{})
        self.assertEqual(resp.status_code, 302)

    def test_get_loggedin_user(self):
        view_class = views.SecuredResourceCreate

        req = RequestFactory().get('/')
        req.META['HTTP_USER_AGENT'] = "Chrome"
        req.user = models.User.objects.last()
        resp = views.SecuredResourceCreate.as_view()(req, *[], **{})
        self.assertEqual(resp.status_code, 200)

    def test_post_Anonymous_user(self):
        view_class = views.SecuredResourceCreate

        req = RequestFactory().post('/')
        req.META['HTTP_USER_AGENT'] = "Chrome"
        req.user = AnonymousUser()

        req_kwargs = { 'Type':1, 'url':'http://google.com', 'file':'' }

        resp = views.SecuredResourceCreate.as_view()(req, *[], **req_kwargs)
        self.assertEqual(resp.status_code, 302)

    def test_post_loggedin_user(self):
        view_class = views.SecuredResourceCreate

        req = RequestFactory().post('/')
        req.META['HTTP_USER_AGENT'] = "Chrome"
        req.user = models.User.objects.last()

        req_kwargs = { 'Type':1, 'url':'http://google.com', 'file':'' }

        resp = views.SecuredResourceCreate.as_view()(req, *[], **req_kwargs)
        self.assertEqual(resp.status_code, 200)
