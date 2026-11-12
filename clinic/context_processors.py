from django.conf import settings
from .models import Appointment

def clinic_global_context(request):
    """Context processor global com contadores e status de configuração de integrações."""
    deepseek_configured = bool(getattr(settings, "DEEPSEEK_API_KEY", None))
    email_configured = bool(getattr(settings, "EMAIL_HOST_USER", None) and getattr(settings, "EMAIL_HOST_PASSWORD", None))
    whatsapp_configured = bool(getattr(settings, "WHATSAPP_API_URL", None) and getattr(settings, "WHATSAPP_API_TOKEN", None))

    return {
        "deepseek_configured": deepseek_configured,
        "email_configured": email_configured,
        "whatsapp_configured": whatsapp_configured,
    }
