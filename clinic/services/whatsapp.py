import logging
import time
import urllib.parse
import webbrowser
from django.conf import settings

logger = logging.getLogger(__name__)


def send_whatsapp_message(phone_number: str, message: str, context: dict = None) -> dict:
    """
    Dispara mensagem de WhatsApp automatizada via interface utilizando PyAutoGUI.
    Abre a conversa no navegador padrão e envia a mensagem.
    Requer que o WhatsApp Web esteja previamente autenticado no navegador padrão.
    """
    try:
        import pyautogui
    except ImportError:
        logger.error("A biblioteca 'pyautogui' não está instalada. Execute: uv add pyautogui")
        return {
            "success": False,
            "message": "Biblioteca pyautogui não instalada. Execute: uv add pyautogui",
            "phone": str(phone_number),
        }

    # 1. Higienização básica do telefone (apenas números com DDI 55)
    clean_phone = "".join(ch for ch in str(phone_number) if ch.isdigit())
    if len(clean_phone) in (10, 11) and not clean_phone.startswith("55"):
        clean_phone = f"55{clean_phone}"

    if not clean_phone:
        return {
            "success": False,
            "message": "Número de telefone inválido ou vazio.",
            "phone": "",
        }

    try:
        # 2. Codifica a mensagem para formato de URL (preserva quebras de linha e acentuação)
        encoded_message = urllib.parse.quote(message)
        whatsapp_url = f"https://web.whatsapp.com/send?phone={clean_phone}&text={encoded_message}"

        logger.info(f"[WHATSAPP PYAUTOGUI] Abrindo WhatsApp Web para {clean_phone}...")
        webbrowser.open(whatsapp_url)

        # 3. Tempo de espera para carregamento da conversa no WhatsApp Web
        time.sleep(12)

        # 4. Pressiona Enter para enviar a mensagem pré-carregada
        pyautogui.press("enter")
        time.sleep(2)

        # 5. Fecha a aba aberta (Ctrl + W) para manter o navegador limpo
        pyautogui.hotkey("ctrl", "w")

        logger.info(f"[WHATSAPP PYAUTOGUI] Mensagem enviada com sucesso para {clean_phone}.")
        return {
            "success": True,
            "message": "Mensagem enviada com sucesso via PyAutoGUI.",
            "phone": clean_phone,
        }

    except Exception as exc:
        logger.error(f"[WHATSAPP PYAUTOGUI] Erro ao disparar mensagem para {clean_phone}: {exc}")
        return {
            "success": False,
            "message": f"Erro durante a automação: {str(exc)}",
            "phone": clean_phone,
        }


def notify_appointment_whatsapp(appointment, action: str = "created") -> dict:
    """
    Gera a mensagem personalizada para o cliente do agendamento e aciona a função de WhatsApp.
    """
    date_str = appointment.scheduled_at.strftime("%d/%m/%Y às %H:%M")
    pet_name = appointment.pet.name
    client_name = appointment.client.name
    vet_name = appointment.professional.name
    vet_crmv = appointment.professional.crmv

    if action == "created":
        text = (
            f" Olá, *{client_name}*!\n\n"
            f"O agendamento do seu pet *{pet_name}* foi realizado com sucesso na *PetCare Clínica Veterinária*!\n\n"
            f" *Data:* {date_str}\n"
            f"‍⚕️ *Veterinário:* {vet_name} ({vet_crmv})\n"
            f" *Motivo:* {appointment.reason}\n\n"
            f"Caso precise remarcar ou tenha alguma dúvida, responda a esta mensagem. Te esperamos! "
        )
    elif action == "completed":
        procedures = appointment.procedures.all()
        proc_list = "\n".join([f"• {p.procedure.name} (x{p.quantity})" for p in procedures]) or "• Consulta padrão"
        text = (
            f" Olá, *{client_name}*!\n\n"
            f"O atendimento de *{pet_name}* com {vet_name} foi finalizado com carinho na *PetCare*!\n\n"
            f"📋 *Procedimentos Realizados:*\n{proc_list}\n\n"
            f"Obrigado pela confiança no cuidado do seu melhor amigo! "
        )
    else:
        text = (
            f" Olá, *{client_name}*! Atualização do agendamento de *{pet_name}*:\n"
            f"Status: *{appointment.get_status_display()}* para {date_str} com {vet_name}."
        )

    return send_whatsapp_message(
        phone_number=appointment.client.phone,
        message=text,
        context={"appointment_id": appointment.id, "action": action}
    )
