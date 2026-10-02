from django.db import models

from django.contrib.auth.models import User

class Client(models.Model):
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name


class Object(models.Model):
    WORK_TYPE_CHOICES = [
        ('facade', 'Утепление фасада'),
        ('roof','Утепление крыши'),
        ('slopes','Утепление откосов'),
        ('seams','Ремонт межпанельных швов'),
        ('drips','Установка оконных отливов'),
        ('canopy','Установка козырька'),
        ('other','Другое'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='objects_list')
    address = models.CharField(max_length=255)
    work_type = models.CharField(max_length=20, choices=WORK_TYPE_CHOICES, default='facade')
    area_m2 = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.address} ({self.client.full_name})"


class Estimate(models.Model):
    object = models.ForeignKey(Object, on_delete=models.CASCADE, related_name='estimates')
    material_name = models.CharField(max_length=255)
    price_per_m2 = models.DecimalField(max_digits=8, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)


    def save(self, *args, **kwargs):
        self.total_amount = self.object.area_m2 * self.price_per_m2
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Смета для {self.object} = {self.total_amount}"


class WorkStage(models.Model):
    STATUS_CHOICES = [
        ('not_started', 'Не начат'),
        ('in_process', 'В работе'),
        ('done', 'Готово'),
    ]

    object = models.ForeignKey(Object, on_delete=models.CASCADE, related_name='stages')
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES,default='not_started')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.get_status_display()} ({self.object})"


class Payment(models.Model):
    METHOD_CHOICES = [
        ('cash', 'наличные'),
        ('card', 'карта'),
        ('transfer', 'перевод'),
    ]

    object = models.ForeignKey(Object, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='cash')
    paid_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Оплата {self.amount} по {self.object}"


class Profile(models.Model):
    ROLE_CHOICES = [
        ('owner', 'Владелец'),
        ('master', 'Мастер'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='master')

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
     