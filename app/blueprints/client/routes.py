# app/blueprints/client/routes.py (VERSÃO FINAL CORRIGIDA E OTIMIZADA)

from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from flask_login import login_required, current_user
# Importações existentes...
from app import db 
from app.models.service import Service
from app.models.booking import Booking
from app.models.schedule import Schedule
from app.services.booking_service import BookingService 
from datetime import datetime, time, timedelta 
from sqlalchemy.orm import joinedload # 🚨 Importação de ferramenta de otimização SQLAlchemy

client_bp = Blueprint('client', __name__)

# =============================================================
# ROTAS PÚBLICAS E DO CLIENTE (sem mudanças)
# =============================================================

@client_bp.route('/')
def index():
    """Rota inicial: Lista serviços (visível para todos)."""
    services = Service.query.all()
    return render_template('client/index.html', services=services)


@client_bp.route('/new-booking/<int:service_id>')
@login_required
def new_booking(service_id):
    """RF05 - Exibe a página de seleção de data e hora para o serviço."""
    service = Service.query.get_or_404(service_id)
    
    # Define a data mínima como o dia seguinte (Regra de negócio: não agendar para hoje)
    min_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

    return render_template(
        'client/new_booking.html', 
        service=service,
        min_date=min_date
    )

# =============================================================
# RF05 - ROTA API PARA BUSCA DE SLOTS DISPONÍVEIS
# =============================================================

@client_bp.route('/api/available_slots', methods=['GET'])
@login_required
def available_slots():
    date_str = request.args.get('date')
    service_id = request.args.get('service_id', type=int)

    if not date_str or not service_id:
        return jsonify({'slots': []})

    try:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        day_of_week = selected_date.weekday()
    except ValueError:
        return jsonify({'slots': []})

    service = Service.query.get(service_id)
    if not service:
        return jsonify({'slots': []})

    service_duration = service.duracao

    # 1. Encontrar os blocos de trabalho (Schedule) para o dia
    schedules = Schedule.query.filter_by(dia_semana=day_of_week).all()

    # 2. Obter agendamentos existentes (Confirmado/Pendente) para a data
    # Usa db.func.date() para o filtro SQL confiável e joinedload para otimizar o acesso à duração
    booked_slots = Booking.query.options(joinedload(Booking.servico)).filter(
        db.func.date(Booking.data_agendamento) == date_str,
        Booking.status.in_(['Confirmado', 'Pendente'])
    ).all()
    
    # Mapeia os horários ocupados para a checagem rápida em Python
    unavailable_intervals = []
    for booked in booked_slots:
        booked_start = booked.data_agendamento
        # Acesso seguro à duração (garantido pelo joinedload)
        booked_duration = booked.servico.duracao
        booked_end = booked_start + timedelta(minutes=booked_duration)
        unavailable_intervals.append((booked_start, booked_end))
    
    available_slots_data = []

    # 3. Gerar slots e checar a disponibilidade
    for schedule in schedules:
        current_time = datetime.combine(selected_date, datetime.strptime(schedule.hora_inicio, '%H:%M').time())
        schedule_end_time = datetime.combine(selected_date, datetime.strptime(schedule.hora_fim, '%H:%M').time())
        
        # Gera os slots no bloco de trabalho
        while current_time < schedule_end_time:
            slot_start = current_time
            slot_end = slot_start + timedelta(minutes=service_duration)
            
            # Garante que o slot inteiro cabe no Schedule
            if slot_end > schedule_end_time:
                break

            is_available = True
            
            # Checagem de conflito (a mesma lógica robusta que agora está em finalize_booking)
            for booked_start, booked_end in unavailable_intervals:
                # Se (Novo Início < Fim do Existente) E (Novo Fim > Início do Existente)
                if (slot_start < booked_end and slot_end > booked_start):
                    is_available = False
                    break
            
            available_slots_data.append({
                'time': slot_start.strftime('%H:%M'),
                'datetime_slot': slot_start.strftime('%Y-%m-%d %H:%M'),
                'status': 'available' if is_available else 'unavailable' 
            })

            # Move para o próximo slot (por exemplo, a cada 30 minutos ou o que for o passo)
            # Assumindo que o avanço é pela duração do serviço, ou um passo fixo (e.g. 30min)
            # Para manter simples, vamos avançar pela duração do serviço.
            # Se você usa um passo fixo (e.g., 30 min) para mostrar a grade, ajuste aqui.
            current_time += timedelta(minutes=service_duration)


    return jsonify({'slots': available_slots_data})

# =============================================================
# RF05 - ROTA DE FINALIZAÇÃO DE AGENDAMENTO (sem mudanças)
# =============================================================

# app/blueprints/client/routes.py

@client_bp.route('/finalize-booking', methods=['POST'])
@login_required
def finalize_booking():
    service_id = request.form.get('service_id', type=int)
    datetime_slot_str = request.form.get('datetime_slot') 
    
    if not service_id or not datetime_slot_str:
        flash('Erro: Serviço ou horário não foram selecionados corretamente.', 'danger')
        return redirect(url_for('client.index'))

    try:
        datetime_slot = datetime.strptime(datetime_slot_str, '%Y-%m-%d %H:%M')
    except ValueError:
        flash('Erro no formato da data/hora selecionada.', 'danger')
        return redirect(url_for('client.index'))
    
    # -------------------------------------------------------------------------
    # 🚨 PASSO CRÍTICO: VERIFICAÇÃO DE CONFLITO COM PYTHON (Server-Side) 🚨
    # -------------------------------------------------------------------------
    
    service = Service.query.get(service_id)
    if not service:
         flash('Serviço não encontrado.', 'danger')
         return redirect(url_for('client.index'))
         
    slot_start = datetime_slot
    slot_end = datetime_slot + timedelta(minutes=service.duracao)
    
    # Formata a data para a string 'YYYY-MM-DD', mais confiável para o filtro SQLite
    booking_date_str = datetime_slot.strftime('%Y-%m-%d')

    # 1. Obter todos os agendamentos existentes (Confirmado/Pendente) para a data
    # Usa db.func.date() para comparar apenas a data, garantindo a correspondência no SQL.
    # Usa joinedload para carregar a duração do serviço de forma otimizada.
    booked_slots = Booking.query.options(joinedload(Booking.servico)).filter(
        db.func.date(Booking.data_agendamento) == booking_date_str, # Filtro SQL confiável
        Booking.status.in_(['Confirmado', 'Pendente']) 
    ).all()
    
    conflito_detectado = False
    
    # 2. Loop para checar sobreposição em Python (totalmente confiável)
    for booked in booked_slots:
        booked_start = booked.data_agendamento
        
        # O acesso à duração é garantido pelo joinedload
        booked_duration = booked.servico.duracao
            
        booked_end = booked_start + timedelta(minutes=booked_duration) 

        # Lógica de sobreposição: (Novo Início < Fim do Existente) E (Novo Fim > Início do Existente)
        if (slot_start < booked_end and slot_end > booked_start):
            conflito_detectado = True
            print(f"CONFLITO DETECTADO (Python Check): Tentativa de agendar {slot_start.strftime('%H:%M')} conflita com Agendamento ID {booked.id} em {booked_start.strftime('%H:%M')}")
            break
            
    if conflito_detectado:
        flash('Este horário ficou indisponível ou há um conflito de horários. Por favor, selecione outro slot.', 'danger')
        return redirect(url_for('client.new_booking', service_id=service_id))
    
    # -------------------------------------------------------------------------
    # FIM DA VERIFICAÇÃO DE CONFLITO
    # -------------------------------------------------------------------------

    # BUSCAR O schedule_id CORRESPONDENTE
    day_of_week = datetime_slot.weekday()
    slot_time_str = datetime_slot.strftime('%H:%M')
    
    schedule = Schedule.query.filter(
        Schedule.dia_semana == day_of_week,
        Schedule.hora_inicio <= slot_time_str,
        Schedule.hora_fim > slot_time_str 
    ).first()

    if not schedule:
        flash('Erro de agendamento: O horário selecionado não corresponde a um bloco de trabalho válido.', 'danger')
        return redirect(url_for('client.new_booking', service_id=service_id))
        
    schedule_id_to_save = schedule.id
    
    # CRIAR E SALVAR (com checagem de exceção)
    try:
        new_booking = Booking(
            user_id=current_user.id,
            service_id=service_id,
            data_agendamento=datetime_slot,
            status='Pendente', 
            schedule_id=schedule_id_to_save 
        )
        
        new_booking.save() 
        
        flash(f'Agendamento de {new_booking.servico.nome} em {datetime_slot.strftime("%d/%m/%Y às %H:%M")} criado com sucesso!', 'success')
        return redirect(url_for('client.my_bookings'))

    except Exception as e:
        flash(f'Falha ao criar agendamento. Tente novamente. Erro: {str(e)}', 'danger')
        return redirect(url_for('client.new_booking', service_id=service_id))
    # -------------------------------------------------------------------------
    # FIM DA VERIFICAÇÃO DE CONFLITO
    # -------------------------------------------------------------------------

    # BUSCAR O schedule_id CORRESPONDENTE
    day_of_week = datetime_slot.weekday()
    slot_time_str = datetime_slot.strftime('%H:%M')
    
    schedule = Schedule.query.filter(
        Schedule.dia_semana == day_of_week,
        Schedule.hora_inicio <= slot_time_str,
        Schedule.hora_fim > slot_time_str 
    ).first()

    if not schedule:
        flash('Erro de agendamento: O horário selecionado não corresponde a um bloco de trabalho válido.', 'danger')
        return redirect(url_for('client.new_booking', service_id=service_id))
        
    schedule_id_to_save = schedule.id
    
    # CRIAR E SALVAR (com checagem de exceção)
    try:
        new_booking = Booking(
            user_id=current_user.id,
            service_id=service_id,
            data_agendamento=datetime_slot,
            status='Pendente', 
            schedule_id=schedule_id_to_save 
        )
        
        new_booking.save() 
        
        flash(f'Agendamento de {new_booking.servico.nome} em {datetime_slot.strftime("%d/%m/%Y às %H:%M")} criado com sucesso!', 'success')
        return redirect(url_for('client.my_bookings'))

    except Exception as e:
        flash(f'Falha ao criar agendamento. Tente novamente. Erro: {str(e)}', 'danger')
        return redirect(url_for('client.new_booking', service_id=service_id))
# =============================================================
# RF06 - ROTA DE MEUS AGENDAMENTOS
# =============================================================

@client_bp.route('/my-bookings')
@login_required
def my_bookings():
    """Exibe todos os agendamentos do usuário logado."""
    
    # 🚨 Adicionar o horário de término (para UX, sem Jinja Filters)
    agendamentos = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.data_agendamento.desc()).all()
    
    agendamentos_com_horario_fim = []
    for booking in agendamentos:
        # Calcula o fim do slot
        end_dt = booking.data_agendamento + timedelta(minutes=booking.servico.duracao)
        
        # Adiciona um novo atributo temporário ao objeto para uso no template
        booking.hora_fim_formatada = end_dt.strftime('%H:%M')
        agendamentos_com_horario_fim.append(booking)
        
    hoje = datetime.now()
    
    return render_template(
        'client/my_bookings.html', 
        agendamentos=agendamentos_com_horario_fim,
        hoje=hoje 
    )
    
# =============================================================
# RF06 - ROTA DE CANCELAMENTO
# =============================================================

@client_bp.route('/cancel-booking/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    """Cancela um agendamento existente se o usuário for o dono."""
    
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.user_id != current_user.id:
        flash('Você não tem permissão para cancelar este agendamento.', 'danger')
        return redirect(url_for('client.my_bookings'))
        
    try:
        booking.cancel() 
        flash(f'Agendamento de {booking.servico.nome} em {booking.data_agendamento.strftime("%d/%m/%Y às %H:%M")} foi cancelado.', 'success')
    except Exception as e:
        flash(f'Falha ao cancelar o agendamento. Erro: {str(e)}', 'danger')
        
    return redirect(url_for('client.my_bookings'))