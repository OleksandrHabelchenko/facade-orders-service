from rest_framework import viewsets

from .models import Client, Object, Estimate, WorkStage, Payment

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

class ObjectViewSet(viewsets.ModelViewSet):
    queryset = Object.objects.all()
    serializer_class = ObjectSerializer

class EstimateViewSet(viewsets.ModelViewSet):
    queryset = Estimate.objects.all()
    serializer_class = EstimateSerializer

class WorkStageViewSet(viewsets.ModelViewSet):
    queryset = WorkStage.objects.all()
    serializer_class = WorkStageSerializer

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer