from django.contrib import admin
from django.urls import path
from django.urls import include
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('admin/', admin.site.urls),
]

urlpatterns += [
    path('api/token-auth/', obtain_auth_token, name='token_auth'),
]

urlpatterns += [
    path('', include('webapp.urls',namespace='webapp')),
    path('api/', include('api.urls',namespace='api')),
]

#Add Django site authentication urls (for login, logout)
urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
]

# Add Static Files
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
