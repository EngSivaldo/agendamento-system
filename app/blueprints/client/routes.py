# app/blueprints/client/routes.py
from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user

from app.models.service import Service
from app.models.booking import Booking
from app.models.schedule import Schedule
from app.services.booking_service import BookingService

client_bp = Blueprint('client', __name__)

@client_bp.route('/')
def index():
    """Rota inicial: Lista serviços (visível para todos)."""
    services = Service.query.all()
    return render_template('client/index.html', services=services)


# Exemplo de rota (em client/routes.py)
from flask_login import current_user

@client_bp.route('/my-bookings')
@login_required
def my_bookings():
    # Busca todos os agendamentos do usuário logado
    agendamentos = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.data_agendamento.desc()).all()
    return render_template('client/my_bookings.html', agendamentos=agendamentos)


# app/blueprints/client/routes.py

# ... (código existente, após my_bookings)

# 🛑 NOVO CÓDIGO AQUI: Rota para agendar um novo serviço (placeholder)
@client_bp.route('/new-booking')
@login_required
def new_booking():
    # Por enquanto, apenas renderiza uma página ou redireciona
    # Esta rota será desenvolvida em detalhes para a RF05.
    
    # Supondo que você terá um template chamado 'new_booking.html'
    return render_template('client/new_booking.html', services=[]) 

# ... (outras rotas)