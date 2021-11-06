from django.urls import path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


shema_view = get_schema_view(
    openapi.Info(
        title="Swipe API",
        default_version='v1',
        description='Swipe API description',
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

url_patterns = [
    # path('swagger(?P<format>\.json|\.yaml)', shema_view.without_ui(cache_timeout=0)),
    path('swagger/', shema_view.with_ui('swagger', cache_timeout=0)),
    path('redoc/', shema_view.with_ui('redoc', cache_timeout=0)),
]