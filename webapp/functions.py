import datetime
import logging
import secrets
import string

from django import forms
from django.http import FileResponse
from django.shortcuts import render
from rest_framework import serializers, status
from rest_framework.response import Response
from securedproj import settings

from .models import TYPES, SecuredResource, SecuredResourceStatistics

# get an instance of a logger
logger = logging.getLogger(__name__)

# ======================================================
# These functions are shared among both webapp and api
# ======================================================


def save(resource):
    return resource.save()


def update_stat(resource, increment=False):
    # update or create stat entry with incrementation of state visited
    stat_objects = SecuredResourceStatistics.objects
    date_today = datetime.date.today()

    if not stat_objects.filter(date=date_today, resource=resource):
        logger.info(
            f"stat for {date_today} does not exist, creating..")

        resource = SecuredResourceStatistics(
            date=datetime.date.today(), resource=resource)

        logger.info(f"stat created, resource id: {resource.resource.id}")

        return save(resource)

    resource = stat_objects.get(date=date_today, resource=resource)

    logger.info(
        f"stat for {date_today} exist, visited occurances: {resource.visited}")

    resource.visited += 1

    logger.info(f"stat incremented, visited: {resource.visited}")
    return save(resource)


def save_secured_resource(resource):

    logger.info(f"saving {TYPES[resource.res_type-1][1]} resource")

    resource_uid = generate_secure_random_string(50)
    password = generate_secure_random_string(10)

    resource.uid = resource_uid
    resource.password = password
    resource.save()

    logger.info(
        f"updating resource stat, id: {resource.id}, uid: {resource.uid}")

    update_stat(resource, False)
    return resource


def generate_secure_random_string(num):
    # generate cruptographically secure random string
    return "".join(
        secrets.choice(string.ascii_uppercase + string.digits) for i in range(num)
    )


def validate_secured_resource(data, is_api=False):

    res_type = data.get("res_type")
    res_file = data.get("res_file")
    url = data.get("url")

    if is_api:
        field_required = "This field is requird."
        if not res_type:
            raise serializers.ValidationError({
                "res_type": field_required
            })

        if res_type == 1 and not url:
            raise serializers.ValidationError({
                "url": field_required
            })

        if res_type == 2 and not res_file:
            raise serializers.ValidationError({
                "res_file": field_required
            })

    if res_type == 1 and not url:
        raise forms.ValidationError("Please enter a URL.")

    if res_type == 2 and not res_file:
        raise forms.ValidationError("Please select a file.")


def resource_exists(uid, request=None, is_api=False):
    resource = SecuredResource.objects.filter(
        uid=uid, status=1)  # status 1 -> active

    if not resource.exists():
        message = "Secured resource not found. Resource expired."
        if is_api:
            return Response({"message": message},
                            status=status.HTTP_404_NOT_FOUND)
        return render(
            request, "error.html",
            context={"message": message}
        )

    return resource.last()


def get_secured_resource(request, password, resource, is_api=False):

    type_index = resource.res_type - 1
    logger.info(
        f"getting {TYPES[type_index][1]} resource, id: {resource.id}, uid: {resource.uid}")

    if password == resource.password:
        update_stat(resource, True)
        if resource.res_type == 2:
            file_name = str(resource.res_file)
            file_details = get_file_details(
                file_name, is_api)  # get file details
            try:
                f = open(f"{settings.MEDIA_ROOT}/{str(file_name)}", "rb")
                response = FileResponse(
                    f, content_type=file_details['content_type'])
                response["Content-Disposition"] = f"{file_details['disposition']};filename={file_name}"

                logger.info(f"file resource {response}")
                return response

            except Exception as e:
                return secured_resource_response("exception", e, "error", request, is_api)
        else:
            logger.info(f"resource returned, url: {resource.url}")
            return secured_resource_response("url", resource.url, "secure_resource", request, is_api)
    else:
        logger.info(f"passwords do not match, id: {resource.id}")
        return secured_resource_response("message", "Passwords do not match.", "error", request, is_api)


def secured_resource_response(key, value, template, request, is_api=False):
    if is_api:
        return Response({key: value})
    return render(request, f"{template}.html", context={key: value})


def get_file_details(file_name, is_api):

    logger.info("getting file details")

    content_type = "application/octet-stream"
    disposition = "attachment"

    if not is_api:
        file_extention = file_name.split(".")[-1].lower()
        file_extentions = {
            "png":  extention_details("png"),
            "jpg":  extention_details("jpeg"),
            "jpeg": extention_details("jpeg"),
            "jpe":  extention_details("jpeg"),
            "gif":  extention_details("gif"),
            "bmp":  extention_details("bmp"),
            "svg":  extention_details("svg+xml"),
            "ico":  extention_details("x-icon"),
            "pdf":  extention_details("pdf")
        }

        if file_extention in file_extentions:
            file_extention = file_extentions[file_extention]
            content_type = file_extention["content_type"]
            disposition = file_extention["disposition"]

    logger.info(
        f"file content type: {content_type}, disposition: {disposition}")

    return {
        "content_type": content_type,
        "disposition": disposition
    }


def extention_details(file_extention):
    if file_extention == "pdf":
        return {"content_type": f"application/{file_extention}", "disposition": "inline"}
    return {"content_type": f"image/{file_extention}", "disposition": "inline"}


def get_secured_resource_model():
    return SecuredResource
