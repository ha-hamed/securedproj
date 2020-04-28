from django.urls import path

from . import views

# for namespace, it is important to avoid name problems in {% url %}
app_name = "api"

urlpatterns = [
    path("get_stat", views.GetStatView.as_view(),
         name="get_stat"),  # authorization token required
    path("secured_resource", views.SecuredResourceView.as_view(),
         name="secured_resource"),  # authorization token required
    path("data/<str:uid>", views.GetSecuredResourceView.as_view(),
         name="data")  # open to anonymous users

]
