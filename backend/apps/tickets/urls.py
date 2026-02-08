from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api.viewsets import CommentViewSet, SLAViewSet, TicketViewSet

router = DefaultRouter()
router.register('tickets', TicketViewSet, basename='ticket')
router.register('comments', CommentViewSet, basename='comment')
router.register('sla', SLAViewSet, basename='sla')

urlpatterns = [
    path('', include(router.urls)),
]
