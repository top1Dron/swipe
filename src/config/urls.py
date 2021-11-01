from django.contrib import admin
from django.urls import path, include
from .yasg import url_patterns as doc_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('auth/', include('djoser.urls.jwt')),
    path('users/', include('users.urls')),
    path('swipe/', include('swipe.urls')),
]

urlpatterns += doc_urls