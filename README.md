# PetCare — Sistema de Clínica Veterinária 🐾

Sistema web completo para gestão veterinária desenvolvido em **Django**, com interface moderna, responsiva e sem sobrecarga visual (clean styling com Tailwind CSS). O foco do sistema é o fluxo de atendimento: **Profissional**, **Cliente (Tutor)**, **Pet**, marcação de **Appointment (Consulta)** e o registro de **Procedures (Procedimentos)** realizadas dentro do agendamento.

Conta também com **Chatbot integrado ao DeepSeek**, notificações por **E-mail**, e serviço com função placeholder estruturada para envio de mensagens via **WhatsApp**.

---

## 🚀 Funcionalidades Principais

1. **Gestão de Agendamentos (Appointments):**
   - Agendamento de consultas com seleção dinâmica de cliente e filtro instantâneo dos seus respectivos pets.
   - Atribuição de veterinário responsável com CRMV e especialidade.
   - Atualização de status da consulta (*Agendado*, *Confirmado*, *Em Andamento*, *Concluído*, *Cancelado*).

2. **Procedimentos Realizados no Atendimento (Procedures):**
   - Registro de procedimentos feitos diretamente dentro de cada agendamento (ex: Vacinação V10, Ultrassom, Hemograma, Profilaxia Dentária, Curativo).
   - Cálculo automático do valor total de procedimentos com suporte a observações clínicas e quantidades.

3. **Cadastro de Tutores e Pets:**
   - Clientes com telefone/WhatsApp, e-mail, CPF e endereço.
   - Pets com espécie (cão, gato, ave, etc.), raça, idade, peso e notas de alergias/cuidados especiais.

4. **Corpo Clínico & Catálogo:**
   - Registro de veterinários com CRMV, especialidade e contatos.
   - Catálogo de procedimentos com valor base e tempo estimado.

5. **Chatbot com DeepSeek IA:**
   - Interface conversacional para tirar dúvidas sobre cuidados com animais, vacinas, horários e serviços da clínica.
   - Conexão nativa com a API do DeepSeek via `DEEPSEEK_API_KEY`.
   - Modo de demonstração inteligente caso a chave ainda não tenha sido preenchida no `.env`.

6. **Notificações por E-mail:**
   - Disparo automático de e-mail HTML estilizado ao criar agendamento ou ao concluir o atendimento.
   - Configuração via `.env` para qualquer provedor SMTP (Gmail, SendGrid, etc.).
   - Fallback gracioso para visualização em console em ambiente de desenvolvimento.

7. **Notificações por WhatsApp (Função Placeholder):**
   - Localizada em `clinic/services/whatsapp.py`: função `send_whatsapp_message(phone_number, message, context)`.
   - Totalmente documentada com instruções detalhadas para plugar qualquer API de WhatsApp (Evolution API, Z-API, Twilio, Meta Cloud API ou Baileys).

---

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python 3.12+ / Django 5.x / 6.x
- **Frontend:** Django Templates + Tailwind CSS (via CDN) + JavaScript Vanilla
- **Banco de Dados:** SQLite (padrão)
- **IA:** DeepSeek API (`deepseek-chat`)
- **E-mail:** Django Mail Engine (SMTP / Console)

---

## ⚙️ Instalação e Execução Local

### 1. Clonar o repositório e criar ambiente virtual

```bash
git clone https://github.com/pedrobellezia/PetCare.git
cd PetCare

python3 -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar variáveis de ambiente (`.env`)

Copie o arquivo de exemplo:
```bash
cp .env.example .env
```

Edite o arquivo `.env` para inserir suas chaves quando desejar:
- `DEEPSEEK_API_KEY`: sua chave da [DeepSeek Platform](https://platform.deepseek.com/).
- `EMAIL_HOST_USER` e `EMAIL_HOST_PASSWORD`: suas credenciais de e-mail (ex: senha de aplicativo do Gmail).
- `WHATSAPP_API_URL` e `WHATSAPP_API_TOKEN`: credenciais do seu provedor de WhatsApp (opcional).

### 4. Executar migrações e popular dados de exemplo

```bash
python manage.py migrate
python manage.py seed_data
```

> **Dados criados pelo `seed_data`:**
> - Superusuário do Django Admin: **`admin`** / senha: **`admin123`**
> - 3 Veterinários (Dra. Camila, Dr. Roberto, Dra. Beatriz)
> - 7 Procedimentos veterinários
> - 4 Clientes com 6 pets cadastrados
> - Agendamentos de exemplo com procedimentos já vinculados

### 5. Iniciar o servidor de desenvolvimento

```bash
python manage.py runserver
```

Acesse no seu navegador: **`http://127.0.0.1:8000/`**
Painel Administrativo: **`http://127.0.0.1:8000/admin/`**

---

## 🧪 Executando os Testes Automatizados

```bash
python manage.py test
```

---

## 📁 Estrutura do Projeto

```text
PetCare/
├── config/                 # Configurações do projeto Django (settings, urls, wsgi)
├── clinic/                 # Aplicação veterinária principal
│   ├── models.py           # Professional, Client, Pet, Procedure, Appointment, AppointmentProcedure
│   ├── views.py            # Views de agendamento, clientes, pets, procedures, chatbot
│   ├── forms.py            # Formulários estilizados com seleção dinâmica
│   ├── admin.py            # Registro dos modelos no Django Admin com inlines
│   ├── urls.py             # Rotas da clínica e endpoints de API
│   ├── services/
│   │   ├── deepseek.py     # Integração com API da DeepSeek + fallback
│   │   ├── email.py        # Envio de emails de confirmação e conclusão
│   │   └── whatsapp.py     # Função placeholder para API de WhatsApp
│   ├── management/
│   │   └── commands/
│   │       └── seed_data.py # Comando para popular banco com dados reais
│   └── tests.py            # Testes unitários e de integração
├── templates/
│   ├── base.html           # Layout base moderno e responsivo com Tailwind
│   └── clinic/
│       ├── dashboard.html  # Painel principal com métricas e próximos atendimentos
│       ├── appointments/   # Listagem, formulário de agendamento e detalhes
│       ├── clients/        # Listagem e perfil do cliente com seus pets
│       ├── pets/           # Cadastro de pets
│       ├── professionals/  # Equipe veterinária
│       ├── procedures/     # Catálogo de procedimentos
│       ├── chat/           # Interface do Chatbot DeepSeek
│       └── emails/         # Template HTML de notificações por e-mail
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 💬 Integração WhatsApp (`clinic/services/whatsapp.py`)

A função `send_whatsapp_message` possui a seguinte assinatura:

```python
def send_whatsapp_message(phone_number: str, message: str, context: dict = None) -> dict:
    ...
```

Ela já higieniza o número, formata o DDI brasileiro e registra logs. Para conectá-la a uma API real (como Evolution API, Z-API ou Meta Cloud API), basta preencher `WHATSAPP_API_URL` e `WHATSAPP_API_TOKEN` no `.env` e descomentar a requisição HTTP demonstrada no corpo da função.
