import logging
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


def send_appointment_email(appointment, action: str = "created") -> bool:
    """
    Envia email formatado para o cliente com detalhes do agendamento.
    Usa configurações de EMAIL_HOST_USER e EMAIL_HOST_PASSWORD do .env.
    """
    if not appointment.client.email:
        logger.warning(f"Agendamento #{appointment.id}: Cliente sem email cadastrado.")
        return False

    client = appointment.client
    pet = appointment.pet
    vet = appointment.professional
    date_str = appointment.scheduled_at.strftime("%d/%m/%Y às %H:%M")

    if action == "created":
        subject = f"[PetCare] Agendamento Confirmado - {pet.name} ({date_str})"
    elif action == "completed":
        subject = f"[PetCare] Atendimento Concluído - {pet.name}"
    else:
        subject = f"[PetCare] Atualização do Agendamento #{appointment.id}"

    context = {
        "appointment": appointment,
        "client": client,
        "pet": pet,
        "professional": vet,
        "date_str": date_str,
        "action": action,
        "procedures": appointment.procedures.all(),
        "total_value": appointment.total_procedures_value,
    }

    try:
        # Renderiza template HTML se existir, senão gera corpo direto
        html_message = render_to_string("clinic/emails/appointment_notification.html", context)
        plain_message = strip_tags(html_message)
    except Exception:
        # Fallback de texto puro
        plain_message = (
            f"Olá {client.name},\n\n"
            f"Seu agendamento na PetCare Clínica Veterinária está confirmado!\n\n"
            f"Pet: {pet.name} ({pet.get_species_display()})\n"
            f"Veterinário: {vet.name} (CRMV: {vet.crmv})\n"
            f"Especialidade: {vet.specialty}\n"
            f"Data e Horário: {date_str}\n"
            f"Motivo: {appointment.reason}\n\n"
            f"Equipe PetCare\n"
            f"Cuidando com amor de quem te faz feliz."
        )
        html_message = None

    try:
        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "PetCare <noreply@petcare.local>")
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=[client.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Email enviado com sucesso para {client.email} referente ao agendamento #{appointment.id}.")
        return True
    except Exception as exc:
        logger.error(f"Erro ao disparar e-mail para {client.email}: {exc}")
        # Não levanta exceção para não interromper a requisição do usuário
        return False
