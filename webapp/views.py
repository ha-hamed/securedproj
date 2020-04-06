from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
from django.urls import reverse
from . import models
from . import forms
from django.views.generic import FormView
from securedproj import settings
from django.views import View
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.utils import timezone

import time
import threading
import datetime as DT
import datetime

WAIT_SECONDS = 60   # run after every 60 seconds before running link disable function
DIFF = DT.timedelta(days=1) # after how much time the link will expire

'''
below code periodically runs a method to check if a link is Older in time so that it will be disabled
(The time is given as argument of timedelta function).
This is kind of Garbage Collector that runs peridically
'''
def destroy_link():
    objs = models.SecuredResource.objects.filter(Status="1")    # Get All Active Objs
    for obj in objs:
        if((obj.DateTime + DIFF) < timezone.now()):
            obj.Status = "2"    # Mark Link as Expired
            obj.save()
    threading.Timer(WAIT_SECONDS, destroy_link).start()
    return

# Run link destroyer Periodically with WAIT_SECONDS Interval
threading.Timer(WAIT_SECONDS, destroy_link).start()

# ====================================
#   Class Based Views
# ====================================
class SecuredResourceCreate(FormView):
    template_name = 'secured_resource.html'
    form_class = forms.SecuredResourceForm

    def get_form_kwargs(self):
        kwargs = super(SecuredResourceCreate, self).get_form_kwargs()
        self.request.user.userstat.LastUserAgent = self.request.META['HTTP_USER_AGENT']
        self.request.user.save()
        return kwargs

    def form_valid(self, form):
        f = form.save()
        self.request.user.userstat.LastUserAgent = self.request.META['HTTP_USER_AGENT']
        self.request.user.save()
        return redirect('webapp:getResult', id=f.id)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

class getResult(View):
    @method_decorator(login_required)
    def get(self, request, id):
        self.request.user.userstat.LastUserAgent = self.request.META['HTTP_USER_AGENT']
        self.request.user.save()

        res = models.SecuredResource.objects.filter(id=id)
        res = res.last()

        context = {
            'password': res.Password,
            "url": request.build_absolute_uri(reverse('webapp:getSecuredResourceFile', kwargs={'UID': res.UID}))
        }
        return render(request, 'resource_created.html', context)

class PasswordView(FormView):
    template_name = 'password.html'
    form_class = forms.PasswordForm

    def get_form_kwargs(self):
        kwargs = super(PasswordView, self).get_form_kwargs()
        if self.request.user.is_authenticated:
            self.request.user.userstat.LastUserAgent = self.request.META['HTTP_USER_AGENT']
            self.request.user.save()
        return kwargs

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            self.request.user.userstat.LastUserAgent = self.request.META['HTTP_USER_AGENT']
            self.request.user.save()

class getSecuredResourceFile(View):
    def get(self, request, UID):
        if self.request.user.is_authenticated:
            self.request.user.userstat.LastUserAgent = self.request.META['HTTP_USER_AGENT']
            self.request.user.save()

        res = models.SecuredResource.objects.filter(UID=UID, Status="1")
        if (res.count() < 1):
            return render(request, "error.html", context={"message": "Not found. Resource expired!"})

        context = { "UID": UID }
        return render(request, 'password.html', context)

    def post(self, request, UID):
        if self.request.user.is_authenticated:
            self.request.user.userstat.LastUserAgent = self.request.META['HTTP_USER_AGENT']
            self.request.user.save()

        res = models.SecuredResource.objects.filter(UID=UID, Status="1")
        if(res.count() < 1):
            return render(request, "error.html", context={"message": "Not found. Resource expired!"})
        res = res.last()

        if request.POST['password'] == res.Password:
            if(models.SecuredResourceStatistics.objects.filter(Date=datetime.date.today(), resource=res).count() > 0 ):
                rs = models.SecuredResourceStatistics.objects.get(Date=datetime.date.today(), resource=res)
                rs.Visited += 1
                rs.save()
            else:
                rs = models.SecuredResourceStatistics(Date=datetime.date.today(), resource=res)
                rs.Visited += 1
                rs.save()

            if res.Type == "2":
                name = str(res.File)
                contentType = 'application/octet-stream'
                try:
                    with open(settings.MEDIA_ROOT + '/' + str(name), 'rb') as file:
                        response = HttpResponse(file.read(), content_type=contentType)
                        response['Content-Disposition'] = 'attachment;filename='+name
                        return response
                except Exception as e:
                    return HttpResponseNotFound('An exception occurred: {}'.format(e))
            else:
                return render(request, "resource.html", { 'url':res.URL })

        else:
            return render(request, "error.html", context={"message": "Passwords do not much."})
