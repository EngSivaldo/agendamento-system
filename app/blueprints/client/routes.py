# app/blueprints/client/routes.py (VERSÃO FINAL COM ROTAS DE PERFIL)

from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash, abort
from flask_login import login_required, current_user
# Importações existentes...
from app import db 
from app.models.service import Service
from app.models.booking import Booking
from app.models.schedule import Schedule
from app.models.user import User # 🚨 Necessário para buscar outros perfis/dados
from app.services.booking_service import BookingService 
from datetime import datetime, time, timedelta 
from sqlalchemy.orm import joinedload 


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
# ... (O CÓDIGO DA ROTA 'available_slots' É MANTIDO INALTERADO) ...
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
    booked_slots = Booking.query.options(joinedload(Booking.servico)).filter(
        db.func.date(Booking.data_agendamento) == date_str,
        Booking.status.in_(['Confirmado', 'Pendente'])
    ).all()
    
    # Mapeia os horários ocupados
    unavailable_intervals = []
    for booked in booked_slots:
        booked_start = booked.data_agendamento
        booked_duration = booked.servico.duracao
        booked_end = booked_start + timedelta(minutes=booked_duration)
        unavailable_intervals.append((booked_start, booked_end))
    
    available_slots_data = []

    # 3. Gerar slots e checar a disponibilidade
    for schedule in schedules:
        current_time = datetime.combine(selected_date, datetime.strptime(schedule.hora_inicio, '%H:%M').time())
        schedule_end_time = datetime.combine(selected_date, datetime.strptime(schedule.hora_fim, '%H:%M').time())
        
        while current_time < schedule_end_time:
            slot_start = current_time
            slot_end = slot_start + timedelta(minutes=service_duration)
            
            if slot_end > schedule_end_time:
                break

            is_available = True
            
            for booked_start, booked_end in unavailable_intervals:
                if (slot_start < booked_end and slot_end > booked_start):
                    is_available = False
                    break
            
            available_slots_data.append({
                'time': slot_start.strftime('%H:%M'),
                'datetime_slot': slot_start.strftime('%Y-%m-%d %H:%M'),
                'status': 'available' if is_available else 'unavailable' 
            })

            current_time += timedelta(minutes=service_duration)

    return jsonify({'slots': available_slots_data})


# =============================================================
# RF05 - ROTA DE FINALIZAÇÃO DE AGENDAMENTO (sem mudanças)
# =============================================================
# ... (O CÓDIGO DA ROTA 'finalize_booking' É MANTIDO INALTERADO) ...
@client_bp.route('/finalize-booking', methods=['POST'])
@login_required
def finalize_booking():
    service_id = request.form.get('service_id', type=int)
    datetime_slot_str = request.form.get('datetime_slot')

    # --- Validação inicial ---
    if not service_id or not datetime_slot_str:
        flash('Erro: Serviço ou horário não foram selecionados corretamente.', 'danger')
        return redirect(url_for('client.index'))

    try:
        datetime_slot = datetime.strptime(datetime_slot_str, '%Y-%m-%d %H:%M')
    except ValueError:
        flash('Erro no formato da data/hora selecionada.', 'danger')
        return redirect(url_for('client.index'))

    # --- Buscar o serviço ---
    service = Service.query.get(service_id)
    if not service:
        flash('Serviço não encontrado.', 'danger')
        return redirect(url_for('client.index'))

    slot_start = datetime_slot
    slot_end = slot_start + timedelta(minutes=service.duracao)
    booking_date_str = datetime_slot.strftime('%Y-%m-%d')

    # --- Buscar agendamentos existentes (Confirmado/Pendente, não deletados) ---
    booked_slots = Booking.query.options(joinedload(Booking.servico)).filter(
        db.func.date(Booking.data_agendamento) == booking_date_str,
        Booking.status.in_(['Confirmado', 'Pendente']),
        Booking.deleted_at.is_(None)
    ).all()

    # --- Checagem de conflito de horário ---
    for booked in booked_slots:
        booked_start = booked.data_agendamento
        booked_end_existing = booked_start + timedelta(minutes=booked.servico.duracao)
        if slot_start < booked_end_existing and slot_end > booked_start:
            flash('Este horário já está ocupado. Por favor, escolha outro slot.', 'danger')
            return redirect(url_for('client.new_booking', service_id=service_id))

    # --- Encontrar Schedule correspondente ---
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

    # --- Criar e salvar o agendamento ---
    new_booking = Booking(
        user_id=current_user.id,
        service_id=service_id,
        data_agendamento=datetime_slot,
        status='Pendente',
        schedule_id=schedule.id
    )

    try:
        new_booking.save()
        flash(f'Agendamento de {new_booking.servico.nome} em {datetime_slot.strftime("%d/%m/%Y às %H:%M")} criado com sucesso!', 'success')
        return redirect(url_for('client.my_bookings'))
    except Exception as e:
        db.session.rollback()
        flash(f'Falha ao criar agendamento. Tente novamente. Erro: {str(e)}', 'danger')
        return redirect(url_for('client.new_booking', service_id=service_id))


# =============================================================
# RF06 - ROTA DE MEUS AGENDAMENTOS (sem mudanças)
# =============================================================
# ... (O CÓDIGO DA ROTA 'my_bookings' É MANTIDO INALTERADO) ...
@client_bp.route('/my-bookings')
@login_required
def my_bookings():
    """Exibe todos os agendamentos do usuário logado."""

    agendamentos = (
        Booking.query
        .options(joinedload(Booking.servico)) 
        .filter(
            Booking.user_id == current_user.id,
            Booking.deleted_at.is_(None) 
        )
        .order_by(Booking.data_agendamento.desc())
        .all()
    )

    agendamentos_com_horario_fim = []

    for booking in agendamentos:
        end_dt = booking.data_agendamento + timedelta(
            minutes=booking.servico.duracao
        )
        booking.hora_fim_formatada = end_dt.strftime('%H:%M')
        agendamentos_com_horario_fim.append(booking)

    hoje = datetime.now()

    return render_template(
        'client/my_bookings.html',
        agendamentos=agendamentos_com_horario_fim,
        hoje=hoje
    )


# =============================================================
# RF06 - ROTA DE CANCELAMENTO (sem mudanças)
# =============================================================
# ... (O CÓDIGO DA ROTA 'cancel_booking' É MANTIDO INALTERADO) ...
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

# =============================================================
# RF06 - ROTA DE EXCLUSÃO DEFINITIVA DE AGENDAMENTO (DELETE REAL) (sem mudanças)
# =============================================================
# ... (O CÓDIGO DA ROTA 'delete_booking' É MANTIDO INALTERADO) ...
@client_bp.route('/delete-booking/<int:booking_id>', methods=['POST'])
@login_required
def delete_booking(booking_id):

    booking = Booking.query.get_or_404(booking_id)

    # 🔐 REGRA CENTRALIZADA NO MODEL
    allowed, reason = booking.can_be_deleted(current_user)

    if not allowed:
        flash(reason, 'warning')
        return redirect(url_for('client.my_bookings'))

    # 📦 Captura antes do soft delete (evita DetachedInstanceError)
    nome_servico = booking.servico.nome
    data_formatada = booking.data_agendamento.strftime('%d/%m/%Y às %H:%M')

    try:
        booking.soft_delete(
            user_id=current_user.id,
            reason='Exclusão solicitada pelo cliente'
        )

        flash(
            f'Agendamento de {nome_servico} em {data_formatada} foi excluído com sucesso.',
            'success'
        )

    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir o agendamento: {str(e)}', 'danger')

    return redirect(url_for('client.my_bookings'))


# =============================================================
# NOVAS ROTAS DE PERFIL DE USUÁRIO
# =============================================================

@client_bp.route('/perfil')
@login_required
def my_profile():
    """Rota de acesso rápido ao perfil do usuário logado."""
    # Redireciona para a rota view_profile com o ID do usuário atual
    return redirect(url_for('client.view_profile', user_id=current_user.id))

@client_bp.route('/perfil/<int:user_id>', methods=['GET'])
@login_required 
def view_profile(user_id):
    """Visualiza o perfil de um usuário específico, requer autorização."""
    
    user_data = User.query.get(user_id)
    
    if user_data is None:
        abort(404)

    # 🔐 REGRA DE AUTORIZAÇÃO:
    # O usuário logado só pode ver o próprio perfil OU deve ser um administrador.
    is_authorized = (current_user.id == user_id) or (current_user.is_admin)

    if not is_authorized:
        # Nega acesso se não for autorizado (403 Forbidden)
        flash('Você não tem permissão para visualizar este perfil.', 'danger')
        abort(403) 
    
    # Busca agendamentos do usuário (apenas os confirmados/pendentes, não excluídos)
    user_bookings = (
        Booking.query
        .options(joinedload(Booking.servico), joinedload(Booking.user))
        .filter(
            Booking.user_id == user_id,
            Booking.status.in_(['Confirmado', 'Pendente']),
            Booking.deleted_at.is_(None)
        )
        .order_by(Booking.data_agendamento.desc())
        .all()
    )

    # O objeto Booking não tem 'hora_fim', então calculamos para exibir no template
    bookings_with_end_time = []
    for booking in user_bookings:
        # Clonamos o objeto para evitar modificar a instância do ORM se for indesejado
        booking_copy = booking
        end_dt = booking.data_agendamento + timedelta(minutes=booking.servico.duracao)
        booking_copy.hora_fim_formatada = end_dt.strftime('%H:%M')
        bookings_with_end_time.append(booking_copy)

    return render_template('user/profile.html', 
                           user=user_data, 
                           bookings=bookings_with_end_time,
                           title=f"Perfil de {user_data.nome}",
                           hoje=datetime.now()) # Passa 'hoje' para comparação de datas no template
    
    
# app/blueprints/client/routes.py

# ... (Seu código existente aqui) ...

# =============================================================
# RFXX - ROTAS DE EDIÇÃO DE PERFIL
# =============================================================


@client_bp.route('/perfil/editar', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Exibe e processa o formulário de edição de perfil do usuário logado."""
    
    # 🚨 NOTA: Se você usa WTForms, o formulário deve ser criado separadamente.
    # Exemplo: form = EditProfileForm(obj=current_user)
    
    # Este é um placeholder, assumindo que você não quer usar um formulário complexo agora.
    # Você deve substituir por um formulário WTForms real.
    
    if request.method == 'POST':
        # Lógica de processamento e validação do formulário POST:
        
        # 1. Atualizar current_user.nome, current_user.email, etc.
        # current_user.nome = request.form.get('nome')
        # ...
        
        # 2. Salvar no banco de dados
        # try:
        #     current_user.save() 
        #     flash('Perfil atualizado com sucesso!', 'success')
        #     return redirect(url_for('client.my_profile'))
        # except Exception as e:
        #     db.session.rollback()
        #     flash(f'Erro ao salvar: {str(e)}', 'danger')
        pass # Implementação completa será feita na criação do formulário
    
    # Retorna o template de edição
    return render_template('user/edit_profile.html', 
                           title='Editar Perfil',
                           user=current_user) # Passa o objeto usuário logado