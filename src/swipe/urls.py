from rest_framework.routers import DefaultRouter
from django.urls import path, include

from swipe import views

router = DefaultRouter()
router.register('houses', views.APIHouseViewSet)
router.register('house_news', views.APIHouseNewsViewSet)
router.register('announcements', views.APIAnnouncementViewSet)
router.register('flats', views.APIFlatViewSet)
router.register('announcement_favourites', views.APIAnnouncementFavouritesViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]