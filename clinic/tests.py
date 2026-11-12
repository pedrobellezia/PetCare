from django.test import TestCase, Client as TestClient
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal
import json

from clinic.models import Professional, Client, Pet, Procedure, Appointment, AppointmentProcedure
from clinic.services.whatsapp import send_whatsapp_message, notify_appointment_whatsapp
from clinic.services.deepseek import ask_deepseek


class PetCareModelsTestCase(TestCase):
    def setUp(self):
        self.professional = Professional.objects.create(
            name="Dra. Camila Santos",
            email="camila@petcare.local",
            phone="(11) 98111-2233",
            crmv="CRMV-SP 24512",
            specialty="Clínica Geral",
        )
        self.client = Client.objects.create(
            name="Mariana Alencar",
            email="mariana@teste.com",
            phone="(11) 97111-0011",
        )
        self.pet = Pet.objects.create(
            client=self.client,
            name="Thor",
            species=Pet.Species.DOG,
            breed="Golden Retriever",
            birth_date=date.today() - timedelta(days=365 * 2),
            weight=Decimal("30.5"),
        )
        self.procedure = Procedure.objects.create(
            name="Consulta Geral",
            default_price=Decimal("120.00"),
            estimated_duration_min=30,
        )

    def test_appointment_creation_and_procedures(self):
        """Testa criação de agendamento e adição de procedures realizadas."""
        appointment = Appointment.objects.create(
            client=self.client,
            pet=self.pet,
            professional=self.professional,
            scheduled_at=timezone.now() + timedelta(days=1),
            reason="Checkup de rotina",
        )

        # Adiciona procedimento ao agendamento
        proc_item = AppointmentProcedure.objects.create(
            appointment=appointment,
            procedure=self.procedure,
            quantity=2,
            price=Decimal("120.00"),
            notes="Realizado com sucesso.",
        )

        self.assertEqual(appointment.procedures.count(), 1)
        self.assertEqual(proc_item.subtotal, Decimal("240.00"))
        self.assertEqual(appointment.total_procedures_value, Decimal("240.00"))

    def test_whatsapp_placeholder_service(self):
        """Testa o comportamento e formato de retorno da função placeholder do WhatsApp."""
        res = send_whatsapp_message("(11) 98765-4321", "Olá, seu agendamento foi confirmado!")
        self.assertTrue(res["success"])
        self.assertIn("phone", res)
        self.assertIn("message", res)

    def test_deepseek_fallback_service(self):
        """Testa resposta de fallback do chatbot quando a chave não estiver configurada."""
        messages = [{"role": "user", "content": "Quais vacinas meu pet precisa?"}]
        res = ask_deepseek(messages)
        self.assertTrue(res["success"])
        self.assertIn("response", res)


class PetCareViewsTestCase(TestCase):
    def setUp(self):
        self.client_http = TestClient()
        self.professional = Professional.objects.create(
            name="Dr. Roberto Lima",
            email="roberto@petcare.local",
            phone="(11) 98222-3344",
            crmv="CRMV-SP 18920",
            specialty="Cirurgia",
        )
        self.client_obj = Client.objects.create(
            name="Lucas Ferreira",
            email="lucas@teste.com",
            phone="(11) 97222-0022",
        )
        self.pet = Pet.objects.create(
            client=self.client_obj,
            name="Bob",
            species=Pet.Species.DOG,
            breed="Vira-lata",
        )
        self.procedure = Procedure.objects.create(
            name="Vacina V10",
            default_price=Decimal("90.00"),
        )
        self.appointment = Appointment.objects.create(
            client=self.client_obj,
            pet=self.pet,
            professional=self.professional,
            scheduled_at=timezone.now() + timedelta(days=2),
            reason="Vacinação",
        )

    def test_dashboard_view(self):
        res = self.client_http.get(reverse("clinic:dashboard"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "PetCare")

    def test_appointment_list_view(self):
        res = self.client_http.get(reverse("clinic:appointment_list"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Bob")

    def test_appointment_detail_and_add_procedure(self):
        url = reverse("clinic:appointment_detail", kwargs={"pk": self.appointment.pk})
        res = self.client_http.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Procedimentos Realizados")

        # Adicionar procedimento via POST
        add_url = reverse("clinic:appointment_add_procedure", kwargs={"pk": self.appointment.pk})
        post_data = {
            "procedure": self.procedure.pk,
            "quantity": 1,
            "price": "90.00",
            "notes": "Primeira dose aplicada",
        }
        res_post = self.client_http.post(add_url, post_data)
        self.assertEqual(res_post.status_code, 302)
        self.assertEqual(self.appointment.procedures.count(), 1)

    def test_api_client_pets(self):
        url = reverse("clinic:api_client_pets", kwargs={"client_id": self.client_obj.pk})
        res = self.client_http.get(url)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(len(data["pets"]), 1)
        self.assertEqual(data["pets"][0]["name"], "Bob")

    def test_api_chat(self):
        url = reverse("clinic:api_chat")
        payload = {
            "messages": [
                {"role": "user", "content": "Olá, qual horário de funcionamento?"}
            ]
        }
        res = self.client_http.post(
            url,
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get("success"))
        self.assertIn("response", data)
