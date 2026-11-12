from django.db import models
from django.utils import timezone
from datetime import date


class Professional(models.Model):
    """Profissional Veterinário / Especialista da clínica."""
    name = models.CharField(max_length=150, verbose_name="Nome Completo")
    email = models.EmailField(unique=True, verbose_name="E-mail")
    phone = models.CharField(max_length=20, verbose_name="Telefone / Celular")
    crmv = models.CharField(max_length=30, unique=True, verbose_name="CRMV (Registro Profissional)")
    specialty = models.CharField(
        max_length=100,
        default="Clínica Geral",
        verbose_name="Especialidade Principal",
        help_text="Ex: Clínica Geral, Dermatologia, Cirurgia, Oftalmologia, etc."
    )
    bio = models.TextField(blank=True, verbose_name="Biografia / Apresentação")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")

    class Meta:
        verbose_name = "Profissional"
        verbose_name_plural = "Profissionais"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.crmv} - {self.specialty})"

    @property
    def total_appointments(self):
        return self.appointments.count()


class Client(models.Model):
    """Cliente (Tutor do Pet)."""
    name = models.CharField(max_length=150, verbose_name="Nome Completo")
    email = models.EmailField(verbose_name="E-mail")
    phone = models.CharField(max_length=20, verbose_name="Telefone / WhatsApp")
    cpf = models.CharField(max_length=20, blank=True, verbose_name="CPF")
    address = models.CharField(max_length=255, blank=True, verbose_name="Endereço")
    notes = models.TextField(blank=True, verbose_name="Observações Gerais")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")

    class Meta:
        verbose_name = "Cliente (Tutor)"
        verbose_name_plural = "Clientes (Tutores)"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.phone})"

    @property
    def pets_count(self):
        return self.pets.count()


class Pet(models.Model):
    """Pet do Cliente / Tutor."""
    class Species(models.TextChoices):
        DOG = "dog", "Cachorro"
        CAT = "cat", "Gato"
        BIRD = "bird", "Ave"
        RODENT = "rodent", "Roedor"
        REPTILE = "reptile", "Réptil"
        OTHER = "other", "Outro"

    class Gender(models.TextChoices):
        MALE = "M", "Macho"
        FEMALE = "F", "Fêmea"

    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="pets",
        verbose_name="Tutor (Cliente)"
    )
    name = models.CharField(max_length=100, verbose_name="Nome do Pet")
    species = models.CharField(
        max_length=20,
        choices=Species.choices,
        default=Species.DOG,
        verbose_name="Espécie"
    )
    breed = models.CharField(max_length=100, blank=True, verbose_name="Raça")
    gender = models.CharField(
        max_length=1,
        choices=Gender.choices,
        default=Gender.MALE,
        verbose_name="Sexo"
    )
    birth_date = models.DateField(null=True, blank=True, verbose_name="Data de Nascimento")
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Peso (kg)"
    )
    allergies_notes = models.TextField(
        blank=True,
        verbose_name="Alergias, Cuidados e Observações"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Cadastrado em")

    class Meta:
        verbose_name = "Pet"
        verbose_name_plural = "Pets"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_species_display()} - Tutor: {self.client.name})"

    @property
    def age_display(self):
        if not self.birth_date:
            return "Idade não informada"
        today = date.today()
        years = today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )
        if years == 0:
            months = (today.year - self.birth_date.year) * 12 + today.month - self.birth_date.month
            return f"{max(months, 1)} mês(es)"
        return f"{years} ano(s)"


class Procedure(models.Model):
    """Procedimento que pode ser realizado em um atendimento."""
    name = models.CharField(max_length=150, unique=True, verbose_name="Nome do Procedimento")
    description = models.TextField(blank=True, verbose_name="Descrição")
    default_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Valor Base (R$)"
    )
    estimated_duration_min = models.PositiveIntegerField(
        default=30,
        verbose_name="Duração Estimada (minutos)"
    )
    is_active = models.BooleanField(default=True, verbose_name="Disponível para Agendamento")

    class Meta:
        verbose_name = "Procedimento"
        verbose_name_plural = "Procedimentos"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} - R$ {self.default_price:.2f}"


class Appointment(models.Model):
    """Agendamento / Consulta Veterinária."""
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Agendado"
        CONFIRMED = "confirmed", "Confirmado"
        IN_PROGRESS = "in_progress", "Em Andamento"
        COMPLETED = "completed", "Concluído"
        CANCELLED = "cancelled", "Cancelado"

    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="appointments",
        verbose_name="Cliente (Tutor)"
    )
    pet = models.ForeignKey(
        Pet,
        on_delete=models.CASCADE,
        related_name="appointments",
        verbose_name="Pet"
    )
    professional = models.ForeignKey(
        Professional,
        on_delete=models.PROTECT,
        related_name="appointments",
        verbose_name="Veterinário Responsável"
    )
    scheduled_at = models.DateTimeField(verbose_name="Data e Horário")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED,
        verbose_name="Status"
    )
    reason = models.TextField(verbose_name="Motivo do Agendamento / Queixa Principal")
    diagnosis = models.TextField(blank=True, verbose_name="Diagnóstico / Avaliação Clínica")
    clinical_notes = models.TextField(blank=True, verbose_name="Prescrições e Orientações")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Agendamento"
        verbose_name_plural = "Agendamentos"
        ordering = ["-scheduled_at"]

    def __str__(self):
        return f"Agendamento #{self.id} - {self.pet.name} ({self.scheduled_at.strftime('%d/%m/%Y %H:%M')})"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.pet_id and self.client_id and self.pet.client_id != self.client_id:
            raise ValidationError({"pet": "O pet selecionado não pertence ao cliente indicado."})

    @property
    def total_procedures_value(self):
        total = sum(item.subtotal for item in self.procedures.all())
        return total

    @property
    def status_badge_class(self):
        badge_map = {
            self.Status.SCHEDULED: "bg-blue-50 text-blue-700 ring-1 ring-blue-700/10",
            self.Status.CONFIRMED: "bg-emerald-50 text-emerald-700 ring-1 ring-emerald-700/10",
            self.Status.IN_PROGRESS: "bg-amber-50 text-amber-700 ring-1 ring-amber-700/10",
            self.Status.COMPLETED: "bg-emerald-100 text-emerald-800 ring-1 ring-emerald-800/10",
            self.Status.CANCELLED: "bg-rose-50 text-rose-700 ring-1 ring-rose-700/10",
        }
        return badge_map.get(self.status, "bg-slate-100 text-slate-700 ring-1 ring-slate-700/10")


class AppointmentProcedure(models.Model):
    """Procedimento realizado dentro de um Agendamento."""
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name="procedures",
        verbose_name="Agendamento"
    )
    procedure = models.ForeignKey(
        Procedure,
        on_delete=models.PROTECT,
        related_name="performed_items",
        verbose_name="Procedimento"
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="Quantidade")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Valor Cobrado (R$)"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Anotações do Procedimento (dosagem, observação clínica, etc.)"
    )
    performed_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Realização")

    class Meta:
        verbose_name = "Procedimento do Agendamento"
        verbose_name_plural = "Procedimentos do Agendamento"
        ordering = ["performed_at"]

    def __str__(self):
        return f"{self.procedure.name} (x{self.quantity}) no Agendamento #{self.appointment_id}"

    @property
    def subtotal(self):
        return self.quantity * self.price

    def save(self, *args, **kwargs):
        # Auto-preenche o preço padrão se não informado
        if self.price is None and self.procedure_id:
            self.price = self.procedure.default_price
        super().save(*args, **kwargs)
