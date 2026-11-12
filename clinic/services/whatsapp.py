import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def send_whatsapp_message(phone_number: str, message: str, context: dict = None) -> dict:
    """
    Função Placeholder para Envio de Mensagens via WhatsApp.
    
    -------------------------------------------------------------------------
    INSTRUÇÕES PARA IMPLEMENTAÇÃO:
    Esta função foi deixada como placeholder para que você integre facilmente
    qualquer provedor de API de WhatsApp de sua preferência (ex: Evolution API,
    Z-API, Twilio, Baileys, ou Meta Cloud API oficial).
    
    O QUE ESTA FUNÇÃO DEVE FAZER:
    1. Higienizar e padronizar o número de telefone:
       - Remover caracteres não numéricos (espaços, traços, parênteses).
       - Garantir o DDI do país (ex: 55 para o Brasil).
       - Exemplo: "(11) 98765-4321" -> "5511987654321".
    
    2. Montar o payload da requisição HTTP:
       - Configurar headers de autenticação (ex: Bearer token ou API key).
       - Corpo JSON contendo o número destinatário e o texto da mensagem.
    
    3. Fazer a chamada POST para o endpoint do provedor configurado no .env:
       - URL configurável via settings.WHATSAPP_API_URL
       - Token configurável via settings.WHATSAPP_API_TOKEN
       - Exemplo prático com 'requests':
           response = requests.post(
               settings.WHATSAPP_API_URL,
               headers={"apikey": settings.WHATSAPP_API_TOKEN, "Content-Type": "application/json"},
               json={"number": clean_phone, "text": message},
               timeout=10
           )
           response.raise_for_status()
           return {"success": True, "data": response.json()}
    
    4. Tratar exceções (Timeout, ConnectionError, HTTPError):
       - Capturar e registrar logs de erro sem quebrar a execução principal da aplicação.
    
    O QUE ESTA FUNÇÃO DEVE RETORNAR:
    Um dicionário com:
       - 'success' (bool): True se a mensagem foi despachada/enviada com sucesso, False em caso de falha.
       - 'message' (str): Descrição ou mensagem de status.
       - 'phone' (str): O telefone destinatário.
       - 'payload' (dict, opcional): Resposta da API do provedor.
    -------------------------------------------------------------------------
    """
    # 1. Higienização básica do telefone
    clean_phone = "".join(ch for ch in str(phone_number) if ch.isdigit())
    if len(clean_phone) in (10, 11) and not clean_phone.startswith("55"):
        clean_phone = f"55{clean_phone}"

    logger.info(
        f"[WHATSAPP PLACEHOLDER] Simulando envio de mensagem WhatsApp para {clean_phone}."
    )
    logger.debug(f"[WHATSAPP PLACEHOLDER] Conteúdo da mensagem:\n{message}")

    # Verifica se as credenciais foram configuradas no .env para dar feedback
    configured = bool(getattr(settings, "WHATSAPP_API_URL", None) and getattr(settings, "WHATSAPP_API_TOKEN", None))

    if not configured:
        # Modo simulação / placeholder ativo
        return {
            "success": True,
            "status": "simulated",
            "phone": clean_phone,
            "provider": "placeholder",
            "message": "Mensagem simulada com sucesso. Configure WHATSAPP_API_URL e WHATSAPP_API_TOKEN no .env para envio real."
        }

    # SE VOCÊ JÁ CONFIGUROU SUAS CHAVES NO .ENV, DESCOMENTE OU COLOQUE AQUI SUA INTEGRAÇÃO REAL:
    # try:
    #     import requests
    #     headers = {
    #         "Authorization": f"Bearer {settings.WHATSAPP_API_TOKEN}",
    #         "Content-Type": "application/json"
    #     }
    #     data = {
    #         "number": clean_phone,
    #         "body": message
    #     }
    #     resp = requests.post(settings.WHATSAPP_API_URL, json=data, headers=headers, timeout=10)
    #     return {"success": resp.ok, "status_code": resp.status_code, "data": resp.json()}
    # except Exception as exc:
    #     logger.error(f"Erro ao enviar WhatsApp: {exc}")
    #     return {"success": False, "error": str(exc)}

    return {
        "success": True,
        "status": "pending_implementation",
        "phone": clean_phone,
        "message": "Função pronta para receber a chamada da sua API de WhatsApp preferida."
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
