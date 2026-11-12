import json
from datetime import datetime, date
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST, require_GET
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.utils import timezone
from django.db.models import Count, Q, Sum

from .models import Professional, Client, Pet, Procedure, Appointment, AppointmentProcedure
from .forms import (
    AppointmentForm,
    AppointmentProcedureForm,
    ClientForm,
    PetForm,
    ProfessionalForm,
    ProcedureForm,
    LoginForm,
    RegisterForm,
)
from .services.email import send_appointment_email
from .services.whatsapp import notify_appointment_whatsapp
from .services.deepseek import ask_deepseek


# ==========================================
# AUTENTICAÇÃO (LOGIN / REGISTRO / LOGOUT)
# ==========================================

def login_view(request):
    """Página de Login do sistema PetCare."""
    if request.user.is_authenticated:
        return redirect("clinic:dashboard")

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Bem-vindo(a) de volta, {user.first_name or user.username}!")
            next_url = request.GET.get("next") or request.POST.get("next")
            return redirect(next_url or "clinic:dashboard")
        else:
            messages.error(request, "Usuário ou senha incorretos. Por favor, verifique.")
    else:
        form = LoginForm(request)

    return render(request, "clinic/auth/login.html", {"form": form})


def register_view(request):
    """Página de Cadastro de novo usuário no PetCare."""
    if request.user.is_authenticated:
        return redirect("clinic:dashboard")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Conta criada com sucesso! Seja bem-vindo(a), {user.first_name or user.username}!")
            return redirect("clinic:dashboard")
        else:
            messages.error(request, "Por favor, corrija os erros abaixo para criar sua conta.")
    else:
        form = RegisterForm()

    return render(request, "clinic/auth/register.html", {"form": form})


def logout_view(request):
    """Encerra a sessão do usuário com segurança."""
    logout(request)
    messages.info(request, "Você encerrou sua sessão com segurança.")
    return redirect("clinic:login")


# ==========================================
# DASHBOARD
# ==========================================

@login_required
def dashboard(request):
    """Página principal / Visão Geral da clínica."""
    today = timezone.localdate()
    
    total_clients = Client.objects.count()
    total_pets = Pet.objects.count()
    total_professionals = Professional.objects.filter(is_active=True).count()
    
    today_appointments_qs = Appointment.objects.filter(scheduled_at__date=today)
    today_count = today_appointments_qs.count()
    
    # Próximos agendamentos
    upcoming_appointments = (
        Appointment.objects.select_related("client", "pet", "professional")
        .prefetch_related("procedures__procedure")
        .filter(scheduled_at__gte=timezone.now())
        .order_by("scheduled_at")[:6]
    )

    # Recentes agendamentos em andamento ou do dia
    recent_activity = (
        Appointment.objects.select_related("client", "pet", "professional")
        .order_by("-scheduled_at")[:5]
    )

    context = {
        "total_clients": total_clients,
        "total_pets": total_pets,
        "total_professionals": total_professionals,
        "today_count": today_count,
        "upcoming_appointments": upcoming_appointments,
        "recent_activity": recent_activity,
        "today": today,
    }
    return render(request, "clinic/dashboard.html", context)


# ==========================================
# AGENDAMENTOS (APPOINTMENTS)
# ==========================================

@login_required
def appointment_list(request):
    """Listagem de agendamentos com filtros."""
    status_filter = request.GET.get("status", "")
    vet_filter = request.GET.get("vet", "")
    date_filter = request.GET.get("date", "")
    search_query = request.GET.get("q", "")

    qs = (
        Appointment.objects.select_related("client", "pet", "professional")
        .prefetch_related("procedures__procedure")
        .all()
    )

    if status_filter:
        qs = qs.filter(status=status_filter)
    if vet_filter:
        qs = qs.filter(professional_id=vet_filter)
    if date_filter:
        try:
            parsed_date = datetime.strptime(date_filter, "%Y-%m-%d").date()
            qs = qs.filter(scheduled_at__date=parsed_date)
        except ValueError:
            pass
    if search_query:
        qs = qs.filter(
            Q(client__name__icontains=search_query) |
            Q(pet__name__icontains=search_query) |
            Q(reason__icontains=search_query)
        )

    qs = qs.order_by("-scheduled_at")

    professionals = Professional.objects.filter(is_active=True)

    context = {
        "appointments": qs,
        "status_choices": Appointment.Status.choices,
        "professionals": professionals,
        "selected_status": status_filter,
        "selected_vet": vet_filter,
        "selected_date": date_filter,
        "search_query": search_query,
    }
    return render(request, "clinic/appointments/list.html", context)


@login_required
def appointment_create(request):
    """Criação de novo agendamento com disparo de e-mail e zap placeholder."""
    initial = {}
    client_id = request.GET.get("client_id")
    pet_id = request.GET.get("pet_id")
    if client_id:
        initial["client"] = client_id
    if pet_id:
        initial["pet"] = pet_id

    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save()
            
            # 1. Envio de e-mail ao cliente
            email_sent = send_appointment_email(appointment, action="created")
            
            # 2. Envio de mensagem WhatsApp placeholder
            zap_result = notify_appointment_whatsapp(appointment, action="created")

            msg = f"Agendamento de {appointment.pet.name} criado com sucesso!"
            if email_sent:
                msg += " E-mail de confirmação enviado."
            if zap_result.get("success"):
                msg += " Notificação WhatsApp disparada."

            messages.success(request, msg)
            return redirect("clinic:appointment_detail", pk=appointment.pk)
    else:
        form = AppointmentForm(initial=initial)

    context = {
        "form": form,
        "title": "Novo Agendamento",
    }
    return render(request, "clinic/appointments/form.html", context)


@login_required
def appointment_detail(request, pk):
    """Visualização detalhada do agendamento, procedures realizadas e histórico."""
    appointment = get_object_or_404(
        Appointment.objects.select_related("client", "pet", "professional")
        .prefetch_related("procedures__procedure"),
        pk=pk
    )
    procedure_form = AppointmentProcedureForm(initial={"appointment": appointment})

    context = {
        "appointment": appointment,
        "procedure_form": procedure_form,
        "status_choices": Appointment.Status.choices,
    }
    return render(request, "clinic/appointments/detail.html", context)


@login_required
def appointment_edit(request, pk):
    """Edição de dados do agendamento."""
    appointment = get_object_or_404(Appointment, pk=pk)

    if request.method == "POST":
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, "Agendamento atualizado com sucesso!")
            return redirect("clinic:appointment_detail", pk=appointment.pk)
    else:
        form = AppointmentForm(instance=appointment)

    context = {
        "form": form,
        "appointment": appointment,
        "title": f"Editar Agendamento #{appointment.pk}",
    }
    return render(request, "clinic/appointments/form.html", context)


@login_required
@require_POST
def appointment_status_update(request, pk):
    """Atualização rápida de status do agendamento."""
    appointment = get_object_or_404(Appointment, pk=pk)
    new_status = request.POST.get("status")

    if new_status in dict(Appointment.Status.choices):
        old_status = appointment.status
        appointment.status = new_status
        appointment.save(update_fields=["status", "updated_at"])

        if new_status == Appointment.Status.COMPLETED and old_status != Appointment.Status.COMPLETED:
            send_appointment_email(appointment, action="completed")
            notify_appointment_whatsapp(appointment, action="completed")
            messages.success(request, "Atendimento concluído! E-mail e WhatsApp de encerramento despachados.")
        else:
            messages.info(request, f"Status atualizado para: {appointment.get_status_display()}")

    return redirect("clinic:appointment_detail", pk=appointment.pk)


# ==========================================
# PROCEDURES REALIZADAS DENTRO DO APPOINTMENT
# ==========================================

@login_required
@require_POST
def appointment_add_procedure(request, pk):
    """Adiciona um procedimento realizado a um agendamento existente."""
    appointment = get_object_or_404(Appointment, pk=pk)
    form = AppointmentProcedureForm(request.POST)

    if form.is_valid():
        proc_item = form.save(commit=False)
        proc_item.appointment = appointment
        if not proc_item.price:
            proc_item.price = proc_item.procedure.default_price
        proc_item.save()
        messages.success(request, f"Procedimento '{proc_item.procedure.name}' adicionado com sucesso ao agendamento!")
    else:
        messages.error(request, "Erro ao registrar procedimento. Verifique os campos informados.")

    return redirect("clinic:appointment_detail", pk=appointment.pk)


@login_required
@require_POST
def appointment_delete_procedure(request, pk, procedure_id):
    """Remove um procedimento registrado no agendamento."""
    appointment = get_object_or_404(Appointment, pk=pk)
    item = get_object_or_404(AppointmentProcedure, pk=procedure_id, appointment=appointment)
    proc_name = item.procedure.name
    item.delete()
    messages.info(request, f"Procedimento '{proc_name}' removido do agendamento.")
    return redirect("clinic:appointment_detail", pk=appointment.pk)


# ==========================================
# CLIENTES & PETS
# ==========================================

@login_required
def client_list(request):
    """Listagem de clientes e seus respectivos pets."""
    q = request.GET.get("q", "")
    clients = Client.objects.prefetch_related("pets").all()
    if q:
        clients = clients.filter(
            Q(name__icontains=q) |
            Q(email__icontains=q) |
            Q(phone__icontains=q) |
            Q(pets__name__icontains=q)
        ).distinct()

    context = {
        "clients": clients,
        "search_query": q,
    }
    return render(request, "clinic/clients/list.html", context)


@login_required
def client_create(request):
    """Cadastro de novo cliente (tutor)."""
    if request.method == "POST":
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save()
            messages.success(request, f"Cliente '{client.name}' cadastrado com sucesso!")
            if "and_pet" in request.POST:
                return redirect(f"/pets/novo/?client_id={client.pk}")
            return redirect("clinic:client_detail", pk=client.pk)
    else:
        form = ClientForm()

    return render(request, "clinic/clients/form.html", {"form": form, "title": "Cadastrar Novo Cliente"})


@login_required
def client_detail(request, pk):
    """Detalhes do cliente, seus pets e histórico de agendamentos."""
    client = get_object_or_404(
        Client.objects.prefetch_related("pets", "appointments__pet", "appointments__professional"),
        pk=pk
    )
    context = {
        "client": client,
        "pets": client.pets.all(),
        "appointments": client.appointments.order_by("-scheduled_at"),
    }
    return render(request, "clinic/clients/detail.html", context)


@login_required
def pet_create(request):
    """Cadastro de pet para um cliente."""
    initial = {}
    client_id = request.GET.get("client_id")
    if client_id:
        initial["client"] = client_id

    if request.method == "POST":
        form = PetForm(request.POST)
        if form.is_valid():
            pet = form.save()
            messages.success(request, f"Pet '{pet.name}' cadastrado com sucesso para o tutor {pet.client.name}!")
            return redirect("clinic:client_detail", pk=pet.client_id)
    else:
        form = PetForm(initial=initial)

    return render(request, "clinic/pets/form.html", {"form": form, "title": "Cadastrar Novo Pet"})


# ==========================================
# PROFISSIONAIS (VETERINÁRIOS)
# ==========================================

@login_required
def professional_list(request):
    """Equipe de veterinários da clínica."""
    vets = Professional.objects.annotate(
        total_appointments_count=Count("appointments")
    ).all()
    return render(request, "clinic/professionals/list.html", {"professionals": vets})


@login_required
def professional_create(request):
    """Cadastro de profissional veterinário."""
    if request.method == "POST":
        form = ProfessionalForm(request.POST)
        if form.is_valid():
            vet = form.save()
            messages.success(request, f"Veterinário(a) '{vet.name}' cadastrado(a) com sucesso!")
            return redirect("clinic:professional_list")
    else:
        form = ProfessionalForm()

    return render(request, "clinic/professionals/form.html", {"form": form, "title": "Cadastrar Profissional"})


# ==========================================
# PROCEDIMENTOS DA CLÍNICA
# ==========================================

@login_required
def procedure_list(request):
    """Catálogo de procedimentos veterinários."""
    procs = Procedure.objects.all()
    return render(request, "clinic/procedures/list.html", {"procedures": procs})


@login_required
def procedure_create(request):
    """Cadastro de novo procedimento no catálogo."""
    if request.method == "POST":
        form = ProcedureForm(request.POST)
        if form.is_valid():
            proc = form.save()
            messages.success(request, f"Procedimento '{proc.name}' criado com sucesso!")
            return redirect("clinic:procedure_list")
    else:
        form = ProcedureForm()

    return render(request, "clinic/procedures/form.html", {"form": form, "title": "Cadastrar Procedimento"})


# ==========================================
# CHATBOT COM DEEPSEEK
# ==========================================

@login_required
def chatbot_view(request):
    """Interface moderna do Chatbot PetCare."""
    return render(request, "clinic/chat/index.html")


@login_required
@require_POST
def api_chat(request):
    """Endpoint JSON que repassa a conversa para o DeepSeek."""
    try:
        data = json.loads(request.body)
        messages_list = data.get("messages", [])
        if not messages_list:
            return JsonResponse({"success": False, "error": "Nenhuma mensagem fornecida."}, status=400)

        result = ask_deepseek(messages_list)
        return JsonResponse(result)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "JSON inválido."}, status=400)
    except Exception as exc:
        return JsonResponse({"success": False, "error": str(exc)}, status=500)


# ==========================================
# APIS AUXILIARES (DINÂMICAS NO FRONT)
# ==========================================

@login_required
@require_GET
def api_client_pets(request, client_id):
    """Retorna JSON dos pets de um cliente específico para atualização no formulário."""
    pets = Pet.objects.filter(client_id=client_id).values("id", "name", "species", "breed")
    return JsonResponse({"pets": list(pets)})


@login_required
@require_GET
def api_procedure_details(request, procedure_id):
    """Retorna dados de valor de um procedimento para auto-preenchimento."""
    proc = get_object_or_404(Procedure, pk=procedure_id)
    return JsonResponse({
        "id": proc.id,
        "name": proc.name,
        "default_price": float(proc.default_price),
        "description": proc.description
    })
