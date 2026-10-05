import pytest

from orders.models import Client, Object, Estimate, WorkStage, Payment, Profile

from django.contrib.auth.models import User

from rest_framework.test import APIClient


@pytest.mark.django_db
class TestClientModel:
    def test_create_client(self):
        client = Client.objects.create(
            full_name="Test Client",
            phone="+491234567890",
        )

        assert client.full_name == "Test Client"
        assert str(client) == "Test Client"


@pytest.mark.django_db
class TestObjectModel:
    def test_create_object(self):
        client = Client.objects.create(
            full_name="Test Client",
            phone="123",
        )
        obj = Object.objects.create(
            client=client,
            work_type="facade",
            address="123 Test Street",
            area_m2=100,
        )

        assert obj.status == "new"
        assert obj.client == client

@pytest.mark.django_db
class TestEstimateModel:
    def test_total_amount_auto_calculated(self):
        client = Client.objects.create(
            full_name="Test Client",
            phone="123",
        )
        obj = Object.objects.create(
            client=client,
            work_type="facade",
            address="123 Test Street",
            area_m2=100,
        )
        estimate = Estimate.objects.create(
            object=obj,
            material_name="Пенопласт",
            price_per_m2=30,
        )

        assert estimate.total_amount == 3000

@pytest.mark.django_db
class TestWorkStageAutoComplete:
    def test_object_completes_when_all_stages_done(self):
        client = Client.objects.create(
            full_name="Test Client",
            phone="123",
        )
        obj = Object.objects.create(
            client=client,
            work_type="facade",
            address="123 Test Street",
            area_m2=100,
        )
        stage1 = WorkStage.objects.create(
            object=obj,
            name="Stage 1",
            status="in_progress",
        )
        
        stage2 = WorkStage.objects.create(
            object=obj,
            name="Stage 2",
            status="in_progress",
        )
        obj.refresh_from_db()
        assert obj.status == "new"

        stage1.status = "done"
        stage1.save()
        obj.refresh_from_db()
        assert obj.status != "completed"

        stage2.status = "done"
        stage2.save()
        obj.refresh_from_db()
        assert obj.status == "completed"
        assert obj.completed_at is not None


@pytest.mark.django_db
class TestPaymentValidation:
    def test_payment_exceeding_estimate_is_rejected(self):
        from orders.serializers import PaymentSerializer

        client = Client.objects.create(
            full_name="Test Client",
            phone="123",
        )
        obj = Object.objects.create(
            client=client,
            work_type="facade",
            address="123 Test Street",
            area_m2=100,
        )
        Estimate.objects.create(
            object=obj,
            material_name="Дюбель-зонт",
            price_per_m2=30,
        )

        serializer = PaymentSerializer(
            data={
                "object": obj.id,
                "amount": 5000.00,
                "method": "cash"
            })
        assert serializer.is_valid() is False

@pytest.mark.django_db
class TestPermissions:
    def setup_method(self):
        self.client_api = APIClient()

        self.owner_user = User.objects.create_user(
            username="owner1", 
            password="pass123"
            )
        Profile.objects.create(
            user=self.owner_user,
            role="owner"
            )
        
        self.master_user = User.objects.create_user(
            username="master1", 
            password="pass123"
            )
        Profile.objects.create(
            user=self.master_user,
            role="master"
            )
    def test_master_cannot_access_clients(self):
        self.client_api.force_authenticate(user=self.master_user)
        response = self.client_api.get("/api/clients/")
        assert response.status_code == 403

    def test_owner_can_access_clients(self):
        self.client_api.force_authenticate(user=self.owner_user)
        response = self.client_api.get("/api/clients/")
        assert response.status_code == 200

    def test_master_can_read_objects(self):
        self.client_api.force_authenticate(user=self.master_user)
        response = self.client_api.get("/api/objects/")
        assert response.status_code == 200

    def test_master_cannot_create_object(self):
        self.client_api.force_authenticate(user=self.master_user)
        response = self.client_api.post("/api/objects/", {
            "client": 1,
            "work_type": "facade",
            "address": "123 Test Street",
            "area_m2": 50,
        })
        assert response.status_code == 403

    def test_unauthenticated_user_gets_401(self):
        response = self.client_api.get("/api/clients/")
        assert response.status_code == 401

    def test_unauthenticated_user_cannot_access_objects(self):
        response = self.client_api.get("/api/objects/")
        assert response.status_code == 401

    def test_owner_can_create_object(self):
        self.client_api.force_authenticate(user=self.owner_user)
        client = Client.objects.create(
            full_name="Test Client",
            phone="123",
        )
        response = self.client_api.post("/api/objects/", {
            "client": client.id,
            "work_type": "facade",
            "address": "123 Test Street",
            "area_m2": 50,
        })
        assert response.status_code == 201

    def test_user_without_profile_is_denied(self):
        user_no_profile = User.objects.create_user(
            username="noprof",
            password="pass123"
        )
        self.client_api.force_authenticate(user=user_no_profile)
        response = self.client_api.get("/api/clients/")
        assert response.status_code == 403

@pytest.mark.django_db
class TestObjectFiltering:
    def setup_method(self):
        self.client_api = APIClient()
        self.owner_user = User.objects.create_user(
            username="owner2", 
            password="pass123"
            )
        Profile.objects.create(
            user=self.owner_user,
            role="owner"
            )
        self.client_api.force_authenticate(user=self.owner_user)

        client = Client.objects.create(
            full_name="Test Client",
            phone="123",
        )
        Object.objects.create(
            client=client,
            work_type="facade",
            address="123 Test Street",
            area_m2=50,
            status="new"
        )
        Object.objects.create(
            client=client,
            work_type="roof",
            address="456 Test Avenue",
            area_m2=75,
            status="completed"
        )

    def test_filter_by_status(self):
        response = self.client_api.get("/api/objects/?status=completed")
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]['address'] == '456 Test Avenue'

    def test_filter_by_work_type(self):
        response = self.client_api.get("/api/objects/?work_type=facade")
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]['address'] == '123 Test Street'

@pytest.mark.django_db
class TestNestedSerializer:
    def test_object_detail_includes_nested_data(self):
        self.client_api = APIClient()
        owner_user = User.objects.create_user(
            username="owner3",
            password="pass123"
        )
        Profile.objects.create(
            user=owner_user,
            role="owner"
        )
        self.client_api.force_authenticate(user=owner_user)

        client = Client.objects.create(
            full_name="Test Client",
            phone="123",
        )
        obj = Object.objects.create(
            client=client,
            work_type="facade",
            address="Addr",
            area_m2=100,
        )
        Estimate.objects.create(
            object=obj,
            material_name="Material",
            price_per_m2=30,
        )
        WorkStage.objects.create(
            object=obj,
            name="Stage 1",
            status="new",
        )

        response = self.client_api.get(f"/api/objects/{obj.id}/")
        assert response.status_code == 200
        assert 'estimates' in response.data
        assert 'stages' in response.data
        assert len(response.data['estimates']) == 1
        assert len(response.data['stages']) == 1

@pytest.mark.django_db
class TestMasterCannotDeleteClient:
    def test_master_cannot_delete_client(self):
        client_api = APIClient()
        master_user = User.objects.create_user(
            username="master2",
            password="pass123"
        )
        Profile.objects.create(
            user=master_user,
            role="master"
        )
        client_api.force_authenticate(user=master_user)

        client = Client.objects.create(
            full_name="Test Client",
            phone="123",
        )

        response = client_api.delete(f"/api/clients/{client.id}/")
        assert response.status_code == 403

@pytest.mark.django_db
class TestPaymentEqualToEstimate:
    def test_payment_exactly_matching_estimate_is_accepted(self):
        from orders.serializers import PaymentSerializer

        client = Client.objects.create(
            full_name="Test Client",
            phone="123",
        )
        obj = Object.objects.create(
            client=client,
            work_type="facade",
            address="Addr",
            area_m2=100,
        )
        Estimate.objects.create(
            object=obj,
            material_name="Дюбель-зонт",
            price_per_m2=30,
        )

        serializer = PaymentSerializer(
            data={
                "object": obj.id,
                "amount": 3000.00,  # Equal to the estimate
                "method": "cash"
            })
        assert serializer.is_valid() is True

        
