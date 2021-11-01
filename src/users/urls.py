from rest_framework.routers import DefaultRouter
from django.urls import path, include

from users import views

router = DefaultRouter()
router.register('developers', views.APIDeveloperViewSet)
router.register('notaries', views.APINotaryViewSet)
router.register('clients', views.APIClientViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
