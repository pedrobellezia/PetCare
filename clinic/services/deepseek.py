import logging
import requests
from django.conf import settings
from clinic.models import Professional, Procedure

logger = logging.getLogger(__name__)


def build_system_prompt() -> str:
    """Monta o prompt de sistema alimentado com o contexto real da clínica."""
    try:
        vets = Professional.objects.filter(is_active=True).values_list("name", "specialty", "crmv")
        vet_info = "\n".join([f"- {name} (CRMV: {crmv}) - Especialidade: {spec}" for name, spec, crmv in vets])
    except Exception:
        vet_info = "Equipe especializada multidisciplinar."

    try:
        procs = Procedure.objects.filter(is_active=True).values_list("name", "default_price")
        proc_info = "\n".join([f"- {name}: R$ {price:.2f}" for name, price in procs])
    except Exception:
        proc_info = "Consultas gerais, vacinação, exames e procedimentos cirúrgicos."

    return (
        "Você é o assistente virtual inteligente da PetCare Clínica Veterinária. "
        "Seu tom é acolhedor, empático, profissional e direto, sem enrolação. "
        "Você ajuda tutores a tirarem dúvidas sobre cuidados gerais com cães, gatos e outros animais de estimação, "
        "explica como funciona o agendamento de consultas na clínica e informa sobre nossos veterinários e procedimentos.\n\n"
        "INFORMAÇÕES DA CLÍNICA:\n"
        f"Veterinários:\n{vet_info}\n\n"
        f"Procedimentos e Valores Base:\n{proc_info}\n\n"
        "Horário de Funcionamento: Segunda a Sexta das 08h às 20h, Sábados das 08h às 14h.\n"
        "Endereço: Av. das Nações Pet, 1200 - Centro.\n"
        "Telefone / WhatsApp: (11) 98765-4321.\n\n"
        "DIRETRIZES DE SAÚDE ANIMAL:\n"
        "- Você NUNCA prescreve medicamentos controlados ou dosagens específicas pela internet.\n"
        "- Em caso de sintomas graves (convulsão, vômito persistente, sangramento, prostração extrema, dificuldade respiratória), "
        "oriente imediatamente o tutor a levar o animal com urgência à clínica ou pronto-socorro veterinário.\n"
        "- Incentive o agendamento de consultas de rotina e vacinação preventiva."
    )


def ask_deepseek(messages: list[dict]) -> dict:
    """
    Envia histórico de mensagens para a API do DeepSeek e retorna a resposta.
    Caso a chave DEEPSEEK_API_KEY ainda não esteja configurada no .env,
    retorna uma resposta informativa e acolhedora indicando que o modo assistente está ativo.
    """
    api_key = getattr(settings, "DEEPSEEK_API_KEY", "").strip()
    api_base = getattr(settings, "DEEPSEEK_API_BASE", "https://api.deepseek.com").strip()
    model = getattr(settings, "DEEPSEEK_MODEL", "deepseek-chat").strip()

    # Se a chave não estiver configurada no .env
    if not api_key:
        last_user_message = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user_message = m.get("content", "").lower()
                break

        # Resposta inteligente local com aviso de configuração
        reply = (
            " Olá! Eu sou o assistente virtual da **PetCare**.\n\n"
            "Atualmente estou em modo de demonstração local. Para respostas completas e dinâmicas geradas pela inteligência artificial DeepSeek, "
            "insira sua chave `DEEPSEEK_API_KEY` no arquivo `.env` da aplicação.\n\n"
            "Posso te ajudar informando que nossa clínica realiza consultas gerais, vacinas, exames e cirurgias com nossos veterinários especializados. "
            "Você pode agendar um horário para o seu pet clicando no botão **Novo Agendamento** no menu superior!"
        )

        if "vacina" in last_user_message:
            reply = (
                "💉 As vacinas essenciais para cães incluem a V8/V10 e a Antirrábica. Para gatos, a Quádrupla ou Quíntupla Felina. "
                "Mantenha a carteirinha sempre em dia! Você pode agendar a vacinação do seu pet pelo nosso painel de agendamentos.\n\n"
                "*(Dica: configure sua DEEPSEEK_API_KEY no .env para ativar a IA em tempo real)*"
            )
        elif "horario" in last_user_message or "hora" in last_user_message:
            reply = (
                " Atendemos de segunda a sexta das 08h às 20h e aos sábados das 08h às 14h. "
                "Você pode agendar um atendimento diretamente pelo sistema no menu **Agendamentos**!"
            )
        elif "emergencia" in last_user_message or "sangue" in last_user_message or "vomito" in last_user_message:
            reply = (
                "⚠️ **Atenção:** Em casos de vômito persistente, desmaios, sangramentos ou prostração intensa, não espere! "
                "Traga seu pet imediatamente à nossa clínica para avaliação presencial de emergência."
            )

        return {
            "success": True,
            "response": reply,
            "configured": False,
        }

    # Chamada real para a API do DeepSeek
    system_prompt = build_system_prompt()
    payload_messages = [{"role": "system", "content": system_prompt}] + messages

    try:
        endpoint = f"{api_base.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": model,
            "messages": payload_messages,
            "temperature": 0.7,
            "max_tokens": 1024,
        }

        resp = requests.post(endpoint, json=data, headers=headers, timeout=30)
        
        if resp.status_code == 200:
            result = resp.json()
            content = result["choices"][0]["message"]["content"]
            return {"success": True, "response": content, "configured": True}
        else:
            logger.error(f"Erro na API DeepSeek (status {resp.status_code}): {resp.text}")
            return {
                "success": False,
                "response": f"Desculpe, ocorreu uma instabilidade na comunicação com a API DeepSeek (HTTP {resp.status_code}). Verifique a chave configurada no .env.",
                "configured": True,
                "error": resp.text
            }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "response": "O serviço de IA demorou para responder. Por favor, tente novamente em instantes.",
            "configured": True
        }
    except Exception as exc:
        logger.error(f"Exceção ao chamar DeepSeek: {exc}")
        return {
            "success": False,
            "response": f"Erro de conexão com o DeepSeek: {exc}",
            "configured": True,
            "error": str(exc)
        }
