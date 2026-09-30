from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import (
    ClientViewSet,
    ObjectViewSet,
    EstimateViewSet,
    WorkStageViewSet,
    PaymentViewSet,
)

router = DefaultRouter()
router.register(r'clients', ClientViewSet)
router.register(r'objects', ObjectViewSet)
router.register(r'estimates', EstimateViewSet)
router.register(r'stages', WorkStageViewSet)
router.register(r'payments', PaymentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]