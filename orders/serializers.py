from rest_framework import serializers

from .models import Client, Object, Estimate, WorkStage, Payment


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'


class ObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Object
        fields = '__all__'

class EstimateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estimate
        fields = '__all__'
        read_only_fields = ['total_amount']

class WorkStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkStage
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

    def validate(self, data):
        obj = data['object']
        total_estimate = sum(e.total_amount for e in obj.estimates.all())
        total_paid = sum(p.amount for p in obj.payments.all())
        new_amount = data['amount']

        if total_paid + new_amount > total_estimate:
            raise serializers.ValidationError(
                "Сумма оплаты превышает сумму сметы для данного объекта."
                )
        return data

class ObjectDetailSerializer(serializers.ModelSerializer):
    estimates = EstimateSerializer(many=True, read_only=True)
    stages = WorkStageSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Object
        fields = '__all__'