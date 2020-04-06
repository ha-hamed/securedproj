from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter
from django.conf.urls import include, re_path

app_name = 'api'    # for namespace. it is important to avoid name problems in {% url %}

urlpatterns = [
    path('GetStat/', views.GetStatView.as_view(), name='GetStat'),      # Authorization token required
    path('SecuredResource/', views.SecuredResourceView.as_view(), name='SecuredResource'),      # Authorization token required
    path('data/<str:UID>', views.GetSecuredResourceView.as_view(), name='data')     # Open to Anonymous Users

]
