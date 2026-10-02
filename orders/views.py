from rest_framework import viewsets

from .models import Client, Object, Estimate, WorkStage, Payment

from .permissions import IsOwner, IsOwnerOrMasterReadOnly

from django_filters.rest_framework import DjangoFilterBackend

from .serializers import (
    ClientSerializer,
    ObjectSerializer,
    EstimateSerializer,
    WorkStageSerializer,
    PaymentSerializer,
)

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsOwner]

class ObjectViewSet(viewsets.ModelViewSet):
    queryset = Object.objects.all()
    serializer_class = ObjectSerializer
    permission_classes = [IsOwnerOrMasterReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'work_type', 'client']

class EstimateViewSet(viewsets.ModelViewSet):
    queryset = Estimate.objects.all()
    serializer_class = EstimateSerializer
    permission_classes = [IsOwner]

class WorkStageViewSet(viewsets.ModelViewSet):
    queryset = WorkStage.objects.all()
    serializer_class = WorkStageSerializer
    permission_classes = [IsOwnerOrMasterReadOnly]

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsOwner]