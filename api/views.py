from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from . import serializers
from webapp import models
from securedproj import settings

import secrets
import string
import datetime
from django.http import FileResponse
from django.db.models import Count
from django.urls import reverse

class SecuredResourceView(APIView):
    permission_classes = (IsAuthenticated,)    # Enabled because it is Open only for Registered User

    def post(self, request):

        self.request.user.userstat.LastUserAgent = self.request.META['HTTP_USER_AGENT']
        self.request.user.save()

        data = request.data

        if(data['Type'] == "1"):
            data['File']= ''
        else:
            data['URL'] = ''

        res = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for i in range(50)) # Generate Cryptographically Secure Random String
        p = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for i in range(10)) # Generate Cryptographically Secure Random String

        # Create an article from the above data
        serializer = serializers.SecuredResourceSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            SecuredResource = serializer.save()

            SecuredResource.UID = res
            SecuredResource.Password = p

            SecuredResource.save()

            if(models.SecuredResourceStatistics.objects.filter(Date=datetime.date.today(), resource=SecuredResource).count() > 0 ):
                pass
            else:
                rs = models.SecuredResourceStatistics(Date=datetime.date.today(), resource=SecuredResource)
                rs.save()

        return Response({
            "url": request.build_absolute_uri(reverse('api:data', kwargs={'UID': SecuredResource.UID})),
            "password": SecuredResource.Password,
        })

class GetSecuredResourceView(APIView):
    # permission_classes = (IsAuthenticated,)       # Disabled because it is Open for Anonymous User
    def post(self, request, UID):
        if(self.request.user.is_authenticated ):
            self.request.user.userstat.LastUserAgent = self.request.META['HTTP_USER_AGENT']
            self.request.user.save()

        data = request.data
        pwd = data['password']

        # Create an object from the above data
        serializer = serializers.SecuredResourceSerializer(data=data)
        if serializer.is_valid(raise_exception=True):

            res = models.SecuredResource.objects.filter(UID=UID, Status="1")
            if (res.count() < 1):
                return Response({"404": "not found"})
            res = res.last()

            if(pwd == res.Password):
                if(models.SecuredResourceStatistics.objects.filter(Date=datetime.date.today(), resource=res).count() > 0 ):
                    rs = models.SecuredResourceStatistics.objects.get(Date=datetime.date.today(), resource=res)
                    rs.Visited += 1
                    rs.save()
                else:
                    rs = models.SecuredResourceStatistics(Date=datetime.date.today(), resource=res)
                    rs.Visited += 1
                    rs.save()

                if (res.Type == "2"):
                    name = str(res.File)
                    contentType = 'application/octet-stream'
                    try:
                        f = open(settings.MEDIA_ROOT + '/' + str(name), 'rb')
                        response = FileResponse(f, content_type=contentType)
                        response['Content-Disposition'] = 'attachment;filename='+name
                        return response
                    except Exception as e:
                        return Response({"exception": '{}'.format(e)})
                else:
                    return Response({"url": str(res.URL)})
            else:
                return Response({"failed": "Wrong password"})

        return Response({"success": "success"})


class GetStatView(APIView):
    permission_classes = (IsAuthenticated,)     # Enabled because it is Open only for Registered User

    def get(self, request):
        dates = models.SecuredResourceStatistics.objects.values('Date').annotate(Count("resource")).order_by()
        content = {}

        for obj in dates:

            Files = models.SecuredResourceStatistics.objects.filter(Date=obj['Date']).exclude(resource__Type="1").annotate(Count("resource")).order_by()
            URLS = models.SecuredResourceStatistics.objects.filter(Date=obj['Date']).exclude(resource__Type="2").annotate(Count("resource")).order_by()

            content[str(obj['Date'])] = {
                "Files": Files.values().aggregate(Count('resource__count'))['resource__count__count'],
                "URLS": URLS.values().aggregate(Count('resource__count'))['resource__count__count'],
                "UnvisitedFiles": Files.filter(Visited=0).values().aggregate(Count('resource__count'))['resource__count__count'],
                "UnvisitedURLs": URLS.filter(Visited=0).values().aggregate(Count('resource__count'))['resource__count__count'],
            }

        return Response(content)
