from django.urls import path

from webapp.views import (CreateSecuredResource, GetResult,
                          GetSecuredResource)

# for namespace, it is important to avoid name problems in {% url %}
app_name = "mainapp"

urlpatterns = [
    # to create new secured resource
    path("", CreateSecuredResource.as_view(),
         name="create_secured_resource"),  # loging required

    # show link and password of created resource
    path("get_result/<int:id>", GetResult.as_view(),
         name="get_result"),  # login Required

    # access saved Secured resource by entering password here
    path("files/<str:uid>", GetSecuredResource.as_view(),
         name="get_secured_resource"),  # open to anonymous users

]
