from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal

from clinic.models import Professional, Client, Pet, Procedure, Appointment, AppointmentProcedure


class Command(BaseCommand):
    help = "Popula o banco de dados com dados iniciais e realistas para a clínica PetCare."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Iniciando população de dados da clínica PetCare..."))

        # 1. Superuser
        User = get_user_model()
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@petcare.local", "admin123")
            self.stdout.write(self.style.SUCCESS("Superusuário criado: admin / admin123"))

        # 2. Profissionais Veterinários
        vets_data = [
            {
                "name": "Dra. Camila Santos",
                "email": "camila.santos@petcare.local",
                "phone": "(11) 98111-2233",
                "crmv": "CRMV-SP 24512",
                "specialty": "Clínica Médica Geral e Felinos",
                "bio": "Especialista em medicina felina e comportamento animal com mais de 8 anos de experiência clínica."
            },
            {
                "name": "Dr. Roberto Lima",
                "email": "roberto.lima@petcare.local",
                "phone": "(11) 98222-3344",
                "crmv": "CRMV-SP 18920",
                "specialty": "Cirurgia Geral e Ortopedia",
                "bio": "Mestre em cirurgia de pequenos animais, focado em procedimentos minimamente invasivos e ortopedia."
            },
            {
                "name": "Dra. Beatriz Costa",
                "email": "beatriz.costa@petcare.local",
                "phone": "(11) 98333-4455",
                "crmv": "CRMV-SP 31045",
                "specialty": "Dermatologia e Alergologia Veterinária",
                "bio": "Dedicada ao diagnóstico e tratamento de atopias, dermatites e alergias cutâneas em cães e gatos."
            },
        ]
        professionals = []
        for vd in vets_data:
            vet, _ = Professional.objects.get_or_create(
                crmv=vd["crmv"],
                defaults=vd
            )
            professionals.append(vet)
        self.stdout.write(self.style.SUCCESS(f"{len(professionals)} veterinários cadastrados."))

        # 3. Procedimentos da Clínica
        procs_data = [
            {
                "name": "Consulta Clínica Geral",
                "description": "Avaliação física completa, ausculta cardiopulmonar, palpação abdominal e anamnese detalhada.",
                "default_price": Decimal("130.00"),
                "estimated_duration_min": 30
            },
            {
                "name": "Vacina Polivalente V10 / V8 (Cães)",
                "description": "Imunização contra Cinomose, Parvovirose, Coronavirose, Hepatite Infecciosa e Leptospirose.",
                "default_price": Decimal("95.00"),
                "estimated_duration_min": 15
            },
            {
                "name": "Vacina Quádrupla Felina (Gatos)",
                "description": "Proteção contra Panleucopenia, Rinotraqueíte, Calicivirose e Clamidiose felina.",
                "default_price": Decimal("105.00"),
                "estimated_duration_min": 15
            },
            {
                "name": "Ultrassonografia Abdominal",
                "description": "Exame de imagem dos órgãos da cavidade abdominal com laudo em tempo real.",
                "default_price": Decimal("220.00"),
                "estimated_duration_min": 45
            },
            {
                "name": "Profilaxia Dentária (Limpeza de Tártaro)",
                "description": "Remoção ultrassônica de cálculo dentário com polimento e avaliação periodontal.",
                "default_price": Decimal("380.00"),
                "estimated_duration_min": 60
            },
            {
                "name": "Hemograma Completo com Plaquetas",
                "description": "Coleta sanguínea e análise laboratorial de série vermelha, branca e contagem de plaquetas.",
                "default_price": Decimal("75.00"),
                "estimated_duration_min": 15
            },
            {
                "name": "Curativo e Tratamento Tópico de Lesão",
                "description": "Higienização antisséptica, debridamento leve e aplicação de pomada regeneradora.",
                "default_price": Decimal("65.00"),
                "estimated_duration_min": 20
            },
        ]
        procedures = []
        for pd in procs_data:
            proc, _ = Procedure.objects.get_or_create(
                name=pd["name"],
                defaults=pd
            )
            procedures.append(proc)
        self.stdout.write(self.style.SUCCESS(f"{len(procedures)} procedimentos cadastrados."))

        # 4. Clientes (Tutores)
        clients_data = [
            {
                "name": "Mariana Alencar",
                "email": "mariana.alencar@exemplo.com",
                "phone": "(11) 97111-0011",
                "cpf": "123.456.789-00",
                "address": "Rua das Flores, 142 - Apto 31",
                "notes": "Prefere atendimentos no período da manhã."
            },
            {
                "name": "Lucas Gabriel Ferreira",
                "email": "lucas.ferreira@exemplo.com",
                "phone": "(11) 97222-0022",
                "cpf": "234.567.890-11",
                "address": "Av. Paulista, 1500",
                "notes": "Tutor de primeira viagem com filhote."
            },
            {
                "name": "Fernanda Ribeiro Rocha",
                "email": "fernanda.rocha@exemplo.com",
                "phone": "(11) 97333-0033",
                "cpf": "345.678.901-22",
                "address": "Rua Oscar Freire, 800",
                "notes": "Tem dois gatos idosos que requerem cuidado especial no manejo."
            },
            {
                "name": "Carlos Eduardo Pinto",
                "email": "carlos.pinto@exemplo.com",
                "phone": "(11) 97444-0044",
                "cpf": "456.789.012-33",
                "address": "Alameda dos Anapurus, 320",
                "notes": ""
            },
        ]
        clients = []
        for cd in clients_data:
            client, _ = Client.objects.get_or_create(
                email=cd["email"],
                defaults=cd
            )
            clients.append(client)
        self.stdout.write(self.style.SUCCESS(f"{len(clients)} clientes cadastrados."))

        # 5. Pets dos Clientes
        pets_data = [
            {
                "client": clients[0],
                "name": "Thor",
                "species": Pet.Species.DOG,
                "breed": "Golden Retriever",
                "gender": Pet.Gender.MALE,
                "birth_date": date.today() - timedelta(days=365 * 3),
                "weight": Decimal("32.5"),
                "allergies_notes": "Alergia a picada de pulga. Dócil e sociável."
            },
            {
                "client": clients[0],
                "name": "Pipoca",
                "species": Pet.Species.DOG,
                "breed": "Spitz Alemão (Lulu)",
                "gender": Pet.Gender.FEMALE,
                "birth_date": date.today() - timedelta(days=365 * 1),
                "weight": Decimal("3.2"),
                "allergies_notes": "Sensibilidade gástrica a rações com corante."
            },
            {
                "client": clients[1],
                "name": "Bob",
                "species": Pet.Species.DOG,
                "breed": "SRD (Vira-lata)",
                "gender": Pet.Gender.MALE,
                "birth_date": date.today() - timedelta(days=180),
                "weight": Decimal("9.0"),
                "allergies_notes": "Filhote muito ativo, vacinação em andamento."
            },
            {
                "client": clients[2],
                "name": "Mia",
                "species": Pet.Species.CAT,
                "breed": "Siamês",
                "gender": Pet.Gender.FEMALE,
                "birth_date": date.today() - timedelta(days=365 * 7),
                "weight": Decimal("4.1"),
                "allergies_notes": "Muito assustada na clínica. Requer toalha e feromônio sintético."
            },
            {
                "client": clients[2],
                "name": "Simba",
                "species": Pet.Species.CAT,
                "breed": "Persa",
                "gender": Pet.Gender.MALE,
                "birth_date": date.today() - timedelta(days=365 * 6),
                "weight": Decimal("4.8"),
                "allergies_notes": "Histórico de cálculo urinário."
            },
            {
                "client": clients[3],
                "name": "Louro",
                "species": Pet.Species.BIRD,
                "breed": "Calopsita",
                "gender": Pet.Gender.MALE,
                "birth_date": date.today() - timedelta(days=365 * 2),
                "weight": Decimal("0.09"),
                "allergies_notes": "Aparação periódica de asas."
            },
        ]
        pets = []
        for pd in pets_data:
            pet, _ = Pet.objects.get_or_create(
                client=pd["client"],
                name=pd["name"],
                defaults=pd
            )
            pets.append(pet)
        self.stdout.write(self.style.SUCCESS(f"{len(pets)} pets cadastrados."))

        # 6. Agendamentos com Procedures Realizadas
        now = timezone.now()

        # Agendamento 1: Concluído (ontem) com procedimentos feitos
        apt1, _ = Appointment.objects.get_or_create(
            client=clients[0],
            pet=pets[0], # Thor
            professional=professionals[0], # Dra. Camila
            scheduled_at=now - timedelta(days=1, hours=2),
            defaults={
                "status": Appointment.Status.COMPLETED,
                "reason": "Consulta de rotina anual e atualização da vacina V10.",
                "diagnosis": "Animal em excelente estado clínico, pelagem íntegra e sem febre.",
                "clinical_notes": "Aplicada vacina V10 no dorso direito. Retornar em 1 ano para reforço."
            }
        )
        if not apt1.procedures.exists():
            AppointmentProcedure.objects.create(
                appointment=apt1,
                procedure=procedures[0], # Consulta
                quantity=1,
                price=procedures[0].default_price,
                notes="Exame físico geral realizado sem anormalidades."
            )
            AppointmentProcedure.objects.create(
                appointment=apt1,
                procedure=procedures[1], # Vacina V10
                quantity=1,
                price=procedures[1].default_price,
                notes="Lote V10-9821, validade 12/2027. Bem tolerada."
            )

        # Agendamento 2: Em andamento / Hoje
        apt2, _ = Appointment.objects.get_or_create(
            client=clients[2],
            pet=pets[3], # Mia
            professional=professionals[2], # Dra. Beatriz (dermato)
            scheduled_at=now.replace(hour=10, minute=30),
            defaults={
                "status": Appointment.Status.IN_PROGRESS,
                "reason": "Coceira excessiva na região do pescoço e perda localizada de pelos.",
                "clinical_notes": "Realizando raspado cutâneo e lâmpada de Wood para descartar fungos."
            }
        )
        if not apt2.procedures.exists():
            AppointmentProcedure.objects.create(
                appointment=apt2,
                procedure=procedures[0], # Consulta
                quantity=1,
                price=procedures[0].default_price,
                notes="Avaliação dermatológica minuciosa."
            )

        # Agendamento 3: Futuro (Amanhã)
        apt3, _ = Appointment.objects.get_or_create(
            client=clients[1],
            pet=pets[2], # Bob
            professional=professionals[0], # Dra. Camila
            scheduled_at=now + timedelta(days=1, hours=4),
            defaults={
                "status": Appointment.Status.SCHEDULED,
                "reason": "Segunda dose de vacina do filhote e orientação nutricional.",
                "clinical_notes": ""
            }
        )

        # Agendamento 4: Futuro (Em 3 dias)
        apt4, _ = Appointment.objects.get_or_create(
            client=clients[0],
            pet=pets[1], # Pipoca
            professional=professionals[1], # Dr. Roberto
            scheduled_at=now + timedelta(days=3, hours=1),
            defaults={
                "status": Appointment.Status.CONFIRMED,
                "reason": "Avaliação prévia para procedimento de limpeza de tártaro.",
                "clinical_notes": ""
            }
        )

        self.stdout.write(self.style.SUCCESS("Agendamentos e procedimentos de exemplo criados com sucesso!"))
        self.stdout.write(self.style.NOTICE("População concluída com sucesso."))
