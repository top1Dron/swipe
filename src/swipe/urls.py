from rest_framework.routers import DefaultRouter
from django.urls import path, include

from swipe import views

app_name = 'swipe'

router = DefaultRouter()
router.register('house', views.houses.APIHouseViewSet)
router.register('house_news', views.houses.APIHouseNewsViewSet)
router.register('announcements', views.announcements.APIAnnouncementViewSet)
router.register('flats', views.flats.APIFlatViewSet)
router.register('promotions', views.announcements.PromotionAPIView)

urlpatterns = [
    path('api/', include(router.urls)),
]