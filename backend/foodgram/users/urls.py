from django.urls import include, path
from rest_framework import routers

from .views import CustomUserViewsSet, SubscriptionViewSet

router = routers.DefaultRouter()
router.register('users', CustomUserViewsSet)

urlpatterns = [
    path('users/subscriptions/', SubscriptionViewSet.as_view({'get': 'list'})),
    path('users/<id>/subscribe/', SubscriptionViewSet.as_view(
        {'post': 'create', 'delete': 'destroy'})
    ),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
]
