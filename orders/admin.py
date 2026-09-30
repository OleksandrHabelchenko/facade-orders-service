from django.contrib import admin

from .models import Client, Object, Estimate, WorkStage, Payment

class EstimateInline(admin.TabularInline):
    model = Estimate
    extra = 0

class WorkstageInline(admin.TabularInline):
    model = WorkStage
    extra = 0

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0

class ObjectAdmin(admin.ModelAdmin):
    inlines = [EstimateInline, WorkstageInline, PaymentInline]


admin.site.register(Client)
admin.site.register(Object, ObjectAdmin)
admin.site.register(Estimate)
admin.site.register(WorkStage)
admin.site.register(Payment)