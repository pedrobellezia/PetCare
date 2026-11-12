from django import forms
from django.utils import timezone
from .models import Professional, Client, Pet, Procedure, Appointment, AppointmentProcedure


class BaseStyledForm(forms.ModelForm):
    """Classe base que aplica estilos consistentes e modernos (sem overdesign) aos widgets."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            widget = field.widget
            current_classes = widget.attrs.get("class", "")
            
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs["class"] = f"{current_classes} h-4 w-4 rounded border-slate-300 text-emerald-600 focus:ring-emerald-500".strip()
            elif isinstance(widget, forms.Textarea):
                widget.attrs["class"] = f"{current_classes} block w-full rounded-lg border-slate-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500 sm:text-sm".strip()
                widget.attrs.setdefault("rows", 3)
            elif isinstance(widget, forms.Select):
                widget.attrs["class"] = f"{current_classes} block w-full rounded-lg border-slate-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500 sm:text-sm bg-white".strip()
            else:
                widget.attrs["class"] = f"{current_classes} block w-full rounded-lg border-slate-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500 sm:text-sm".strip()


class AppointmentForm(BaseStyledForm):
    scheduled_at = forms.DateTimeField(
        label="Data e Horário",
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"},
            format="%Y-%m-%dT%H:%M"
        ),
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"]
    )

    class Meta:
        model = Appointment
        fields = [
            "client",
            "pet",
            "professional",
            "scheduled_at",
            "status",
            "reason",
            "clinical_notes"
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["professional"].queryset = Professional.objects.filter(is_active=True)
        self.fields["client"].empty_label = "Selecione o Cliente (Tutor)..."
        self.fields["pet"].empty_label = "Selecione o Pet..."
        self.fields["professional"].empty_label = "Selecione o Veterinário..."
        
        # Se um cliente já estiver selecionado (ex: edição ou post), filtra os pets
        if "client" in self.data:
            try:
                client_id = int(self.data.get("client"))
                self.fields["pet"].queryset = Pet.objects.filter(client_id=client_id)
            except (ValueError, TypeError):
                self.fields["pet"].queryset = Pet.objects.none()
        elif self.instance.pk and self.instance.client_id:
            self.fields["pet"].queryset = self.instance.client.pets.all()
        else:
            self.fields["pet"].queryset = Pet.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        client = cleaned_data.get("client")
        pet = cleaned_data.get("pet")
        if client and pet and pet.client_id != client.id:
            self.add_error("pet", f"O pet '{pet.name}' pertence a outro tutor ({pet.client.name}).")
        return cleaned_data


class AppointmentProcedureForm(BaseStyledForm):
    class Meta:
        model = AppointmentProcedure
        fields = ["procedure", "quantity", "price", "notes"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["procedure"].queryset = Procedure.objects.filter(is_active=True)
        self.fields["procedure"].empty_label = "Selecione o Procedimento..."
        self.fields["price"].widget.attrs.setdefault("placeholder", "Ex: 120.00 (deixe em branco p/ valor base)")
        self.fields["price"].required = False


class ClientForm(BaseStyledForm):
    class Meta:
        model = Client
        fields = ["name", "email", "phone", "cpf", "address", "notes"]
        widgets = {
            "phone": forms.TextInput(attrs={"placeholder": "(11) 98765-4321"}),
            "cpf": forms.TextInput(attrs={"placeholder": "000.000.000-00"}),
            "address": forms.TextInput(attrs={"placeholder": "Rua, Número, Bairro, Cidade"}),
        }


class PetForm(BaseStyledForm):
    birth_date = forms.DateField(
        label="Data de Nascimento (Aproximada)",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"})
    )

    class Meta:
        model = Pet
        fields = ["client", "name", "species", "breed", "gender", "birth_date", "weight", "allergies_notes"]
        widgets = {
            "weight": forms.NumberInput(attrs={"step": "0.1", "placeholder": "Peso em kg (ex: 7.5)"}),
            "breed": forms.TextInput(attrs={"placeholder": "Ex: Labrador, SRD (Vira-lata), Siamês"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["client"].empty_label = "Selecione o Tutor..."


class ProfessionalForm(BaseStyledForm):
    class Meta:
        model = Professional
        fields = ["name", "email", "phone", "crmv", "specialty", "bio", "is_active"]
        widgets = {
            "crmv": forms.TextInput(attrs={"placeholder": "Ex: CRMV-SP 12345"}),
            "specialty": forms.TextInput(attrs={"placeholder": "Ex: Clínica Geral, Cirurgia, Dermatologia"}),
            "phone": forms.TextInput(attrs={"placeholder": "(11) 98765-4321"}),
        }


class ProcedureForm(BaseStyledForm):
    class Meta:
        model = Procedure
        fields = ["name", "description", "default_price", "estimated_duration_min", "is_active"]
        widgets = {
            "default_price": forms.NumberInput(attrs={"step": "0.01", "placeholder": "150.00"}),
            "estimated_duration_min": forms.NumberInput(attrs={"step": "5", "placeholder": "30"}),
        }
