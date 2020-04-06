from django.urls import path
from . import views

app_name = 'mainapp'    # For namespace. it is important to avoid name problems in {% url %}

urlpatterns = [
    # To create new Secured Resource
    path('', views.SecuredResourceCreate.as_view(),name='SecuredResourceCreate'), # Login Required

    # Show Link and Password of created Resource
    path('GetResult/<int:id>', views.getResult.as_view(),name='getResult'), # Login Required

    # Access saved Secured resource by entering password here
    path('files/<str:UID>', views.getSecuredResourceFile.as_view(),name='getSecuredResourceFile'), # Open to Anonymous Users

]
