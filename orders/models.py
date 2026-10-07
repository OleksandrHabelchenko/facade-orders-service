from django.db import models

from django.contrib.auth.models import User

from django.utils import timezone

from django.core.exceptions import ValidationError

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

    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('estimate', 'Смета готова'),
        ('in_process', 'В работе'),
        ('completed', 'Завершен'),
        ('paid', 'Оплачен'),
    ]

    UNIT_CHOICES = [
        ('m2', 'м²'),
        ('m_p', 'п.м.'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='objects_list')
    address = models.CharField(max_length=255)
    work_type = models.CharField(max_length=20, choices=WORK_TYPE_CHOICES, default='facade')
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='m2')
    area_m2 = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    area_m_p = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.address} ({self.client.full_name})"


class Estimate(models.Model):
    object = models.ForeignKey(Object, on_delete=models.CASCADE, related_name='estimates')
    material_name = models.CharField(max_length=255)
    price_per_m2 = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    price_per_m_p = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)


    def clean(self):
        if self.object.unit == 'm2':
            if not self.object.area_m2 or not self.price_per_m2:
                raise ValidationError("Площадь в м² или цена за м² не указана для объекта.")
        elif self.object.unit == 'm_p':
            if not self.object.area_m_p or not self.price_per_m_p:
                raise ValidationError("Площадь в п.м. или цена за п.м. не указана для объекта.")


    def save(self, *args, **kwargs):
        self.full_clean()  # Вызываем clean() перед сохранением
        if self.object.unit == 'm2':
            self.total_amount = self.price_per_m2 * self.object.area_m2
        elif self.object.unit == 'm_p':
            self.total_amount = self.price_per_m_p * self.object.area_m_p
        super().save(*args, **kwargs)
        if self.object.status == 'new':
            self.object.status = 'estimate'
            self.object.save()

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
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    def clean(self):
        duplicate = WorkStage.objects.filter(
            object=self.object, name__iexact=self.name
        ).exclude(pk=self.pk).exists()
        if duplicate:
            raise ValidationError(f"Этап с именем '{self.name}' уже существует для данного объекта.")

    def save(self, *args, **kwargs):
        self.full_clean()
        if self.status == 'in_process' and not self.start_date:
            self.start_date = timezone.now()
        if self.status == 'done' and not self.end_date:
            self.end_date = timezone.now()
        super().save(*args, **kwargs)
        stages = self.object.stages.all()
        if stages.exists() and all(s.status == 'done' for s in stages):
            self.object.status = 'completed'
            self.object.completed_at = timezone.now()
            self.object.save()

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
     