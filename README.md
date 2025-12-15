# 📅 Sistema de Agendamento

Sistema web de agendamento desenvolvido com **Flask**, seguindo boas práticas de
engenharia de software, arquitetura modular e padrão _Application Factory_.

---

## 🚀 Tecnologias Utilizadas

- Python 3.11+
- Flask
- Flask-SQLAlchemy
- Flask-Migrate
- SQLite (desenvolvimento)
- Bootstrap (frontend)
- PowerShell / Git

---

## 📁 Estrutura do Projeto

agendamento_system/
│
├── app/
│ ├── init.py
│ ├── routes/
│ ├── models/
│ ├── templates/
│ └── static/
│
├── instance/
├── migrations/
├── venv/
│
├── run.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md

---

## ⚙️ Como Executar o Projeto

### 1️⃣ Criar ambiente virtual

```bash
python -m venv venv
venv\Scripts\activate
```

pip install -r requirements.txt

FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=dev-secret-key

flask run

👨‍💻 Autor

Projeto desenvolvido para fins acadêmicos e profissionais.

✔️ **Salve o arquivo.**

---

# 4️⃣ `.env` — Configuração correta

Abra o `.env` e cole:

```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=super-secret-key-dev
```
