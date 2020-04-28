import datetime
import logging
import threading

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import FormView

from . import forms
from .functions import get_secured_resource, resource_exists
from .models import SecuredResource

WAIT_SECONDS = 60   # run after every 60 seconds before running link disable function
DIFF = datetime.timedelta(days=1)  # after how much time the link will expire

'''
below code periodically runs a method to check if a link is Older in time so that it will be disabled
(The time is given as argument of timedelta function).
This is kind of Garbage Collector that runs peridically
'''

# get an instance of a logger
logger = logging.getLogger(__name__)


def destroy_link():

    logger.info(
        "disabling all expired resources, setting their status to expired..")

    objects = SecuredResource.objects.filter(
        status=1, date__lte=timezone.now() - DIFF).update(status=2)

    if objects:
        logger.info(f"set {objects} resources expired")
    logger.info("no expired resources found")

    threading.Timer(WAIT_SECONDS, destroy_link).start()
    return


# run link destroyer periodically with WAIT_SECONDS Interval
threading.Timer(WAIT_SECONDS, destroy_link).start()

# =========================
#   Class Based Views
# =========================


class CreateSecuredResource(FormView):
    template_name = "create_secure_resource.html"
    form_class = forms.SecuredResourceForm

    def get_form_kwargs(self):
        return super(CreateSecuredResource, self).get_form_kwargs()

    def form_valid(self, form):
        f = form.save()
        self.inst = f
        return redirect("webapp:get_result", id=f.id)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse("webapp:get_result", kwargs={"id": self.inst.id})


class GetResult(View):
    @method_decorator(login_required)
    def get(self, request, id):
        res = SecuredResource.objects.filter(id=id)
        res = res.last()

        context = {
            "password": res.password,
            "url": request.build_absolute_uri(reverse(
                "webapp:get_secured_resource", kwargs={"uid": res.uid}))
        }

        return render(request, "resource.html", context)


class PasswordView(FormView):
    template_name = "password.html"
    form_class = forms.PasswordForm


class GetSecuredResource(View):
    def get(self, request, uid):
        resource_exists(uid, request)
        return render(request, "password.html", context={"uid": uid})

    def post(self, request, uid):
        resource = resource_exists(uid, request)
        return get_secured_resource(request, request.POST["password"], resource)
