from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api.viewsets import (
    AcceptInvitationView,
    BusinessCalendarViewSet,
    InvitationViewSet,
    MeView,
    OrganizationViewSet,
    RegisterView,
    VerifyEmailView,
)

router = DefaultRouter()
router.register('invitations', InvitationViewSet, basename='invitation')

urlpatterns = [
    path('me/', MeView.as_view({'get': 'list'}), name='me'),
    path('register/', RegisterView.as_view({'post': 'create'}), name='register'),
    path('verify-email/', VerifyEmailView.as_view({'post': 'create'}), name='verify-email'),
    path('accept-invitation/', AcceptInvitationView.as_view({'post': 'create'}), name='accept-invitation'),
    path('organization/', OrganizationViewSet.as_view({'get': 'list', 'patch': 'partial_update'}), name='organization'),
    path('business-calendar/', BusinessCalendarViewSet.as_view({'get': 'list', 'patch': 'partial_update'}), name='business-calendar'),
    path('', include(router.urls)),
]
