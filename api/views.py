import logging

from django.db.models import Count
from django.urls import reverse
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from webapp.models import SecuredResourceStatistics
from webapp.functions import (get_secured_resource, resource_exists,
                              save_secured_resource)

from . import serializers

# get an instance of a logger
logger = logging.getLogger(__name__)


class SecuredResourceView(APIView):
    # enabled because it is open only to registered users
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = serializers.SecuredResourceSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):

            secured_resource = serializer.save()    # create an article from above data
            save_secured_resource(secured_resource)

        return Response({
            "url": request.build_absolute_uri(
                reverse("api:data", kwargs={"uid": secured_resource.uid})),
            "password": secured_resource.password
        })


class GetSecuredResourceView(APIView):

    def post(self, request, uid):

        data = request.data
        serializer = serializers.PasswordSerializer(
            data=data)  # create an object from above data

        if serializer.is_valid(raise_exception=True):
            resource = resource_exists(uid, None, is_api=True)
            return get_secured_resource(None, data["password"], resource, True)


class GetStatView(APIView):
    # enabled because it is Open only for Registered User
    permission_classes = (IsAuthenticated,)

    def get(self, request):

        logger.info("getting stats of resource of each type, added every day")

        secured_resource_stats = SecuredResourceStatistics.objects \
            .values('date').annotate(Count("resource")).order_by()

        content = {}

        for resource in secured_resource_stats:

            files = self.get_filter(1, resource)  # exclude url resources type
            urls = self.get_filter(2, resource)  # exclude file resources type

            content[str(resource["date"])] = {
                "files": self.aggregate(files.values()),
                "urls": self.aggregate(urls.values()),
                "unvisited_files": self.aggregate(self.get_filter_unvisited(files)),
                "unvisited_urls": self.aggregate(self.get_filter_unvisited(urls))
            }

        logger.info(f"stats: {content}")

        return Response(content)

    @staticmethod
    def get_filter(res_type, resource):
        return SecuredResourceStatistics.objects.filter(
            date=resource["date"]).exclude(resource__res_type=res_type) \
            .annotate(Count("resource")).order_by()

    @staticmethod
    def get_filter_unvisited(resources):
        return resources.filter(visited=0).values()

    @staticmethod
    def aggregate(values):
        return values.aggregate(Count("resource__count"))["resource__count__count"]
