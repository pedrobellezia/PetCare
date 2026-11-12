from django.urls import path
from . import views

app_name = "clinic"

urlpatterns = [
    # Autenticação
    path("login/", views.login_view, name="login"),
    path("cadastro/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),

    # Dashboard
    path("", views.dashboard, name="dashboard"),
    
    # Agendamentos
    path("agendamentos/", views.appointment_list, name="appointment_list"),
    path("agendamentos/novo/", views.appointment_create, name="appointment_create"),
    path("agendamentos/<int:pk>/", views.appointment_detail, name="appointment_detail"),
    path("agendamentos/<int:pk>/editar/", views.appointment_edit, name="appointment_edit"),
    path("agendamentos/<int:pk>/status/", views.appointment_status_update, name="appointment_status_update"),
    
    # Procedures do Agendamento
    path("agendamentos/<int:pk>/procedimentos/adicionar/", views.appointment_add_procedure, name="appointment_add_procedure"),
    path("agendamentos/<int:pk>/procedimentos/<int:procedure_id>/remover/", views.appointment_delete_procedure, name="appointment_delete_procedure"),

    # Clientes
    path("clientes/", views.client_list, name="client_list"),
    path("clientes/novo/", views.client_create, name="client_create"),
    path("clientes/<int:pk>/", views.client_detail, name="client_detail"),

    # Pets
    path("pets/novo/", views.pet_create, name="pet_create"),

    # Profissionais
    path("profissionais/", views.professional_list, name="professional_list"),
    path("profissionais/novo/", views.professional_create, name="professional_create"),

    # Procedimentos Gerais
    path("procedimentos/", views.procedure_list, name="procedure_list"),
    path("procedimentos/novo/", views.procedure_create, name="procedure_create"),

    # Chatbot com DeepSeek
    path("chat/", views.chatbot_view, name="chatbot"),
    path("api/chat/", views.api_chat, name="api_chat"),

    # Endpoints utilitários
    path("api/client/<int:client_id>/pets/", views.api_client_pets, name="api_client_pets"),
    path("api/procedure/<int:procedure_id>/details/", views.api_procedure_details, name="api_procedure_details"),
]
