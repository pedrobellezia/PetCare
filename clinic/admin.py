from django.contrib import admin
from .models import Professional, Client, Pet, Procedure, Appointment, AppointmentProcedure


class PetInline(admin.TabularInline):
    model = Pet
    extra = 1
    fields = ("name", "species", "breed", "gender", "birth_date", "weight")


class AppointmentProcedureInline(admin.TabularInline):
    model = AppointmentProcedure
    extra = 1
    fields = ("procedure", "quantity", "price", "notes")
    autocomplete_fields = ["procedure"]


@admin.register(Professional)
class ProfessionalAdmin(admin.ModelAdmin):
    list_display = ("name", "crmv", "specialty", "phone", "email", "is_active", "created_at")
    list_filter = ("specialty", "is_active")
    search_fields = ("name", "crmv", "email", "phone")


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "email", "cpf", "pets_count", "created_at")
    search_fields = ("name", "phone", "email", "cpf")
    inlines = [PetInline]


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ("name", "species", "breed", "client", "gender", "weight", "birth_date")
    list_filter = ("species", "gender")
    search_fields = ("name", "breed", "client__name", "client__phone")
    autocomplete_fields = ["client"]


@admin.register(Procedure)
class ProcedureAdmin(admin.ModelAdmin):
    list_display = ("name", "default_price", "estimated_duration_min", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "description")


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("id", "scheduled_at", "pet", "client", "professional", "status", "total_procedures_value")
    list_filter = ("status", "professional", "scheduled_at")
    search_fields = ("pet__name", "client__name", "reason", "professional__name")
    autocomplete_fields = ["client", "pet", "professional"]
    inlines = [AppointmentProcedureInline]
    date_hierarchy = "scheduled_at"


@admin.register(AppointmentProcedure)
class AppointmentProcedureAdmin(admin.ModelAdmin):
    list_display = ("appointment", "procedure", "quantity", "price", "subtotal", "performed_at")
    list_filter = ("procedure", "performed_at")
    search_fields = ("appointment__pet__name", "procedure__name", "notes")
