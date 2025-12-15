# app/blueprints/admin/routes.py (Continuação)

from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.utils.decorators import admin_required 
from flask_login import login_required
from app.models.user import User
from app.models.service import Service 
from app.models.booking import Booking
from app.models.schedule import Schedule 
from flask_login import login_required # Importa o decorator padrão do Flask-Login
from app.utils.decorators import admin_required # Importa apenas o seu decorator customizado

# -------------------------------------------------------------
# DEFINIÇÃO DO BLUEPRINT (ESTE BLOCO É CRUCIAL E DEVE VIR PRIMEIRO)
# -------------------------------------------------------------
admin_bp = Blueprint('admin', __name__) 
# -------------------------------------------------------------
# -------------------------------------------------------------



@admin_bp.route('/') # Mapeia para /admin
@admin_required
def dashboard():
    """RF08 - Dashboard Administrativo: Exibe informações de resumo."""
    
    # 1. Obter dados de resumo para o Dashboard (RF08)
    total_services = Service.query.count()
    total_users = User.query.count()
    # Adicione uma lógica de contagem de agendamentos se desejar
    total_bookings = Booking.query.count() 
    
    # 2. Renderizar o template
    return render_template('admin/dashboard.html',
                           total_services=total_services,
                           total_users=total_users,
                           total_bookings=total_bookings)
# ROTAS DE SERVIÇOS (CRUD - RF03)
# -------------------------------------------------------------



@admin_bp.route('/services')
@admin_required
def manage_services():
    """RF03 - Exibe a lista de todos os serviços."""
    services = Service.query.all()
    return render_template('admin/services.html', services=services)



@admin_bp.route('/services/new', methods=['GET', 'POST'])
@admin_required
def new_service():
    """RF03 - Cria um novo serviço."""
    if request.method == 'POST':
        nome = request.form.get('nome')
        descricao = request.form.get('descricao')
        # Garantir que a duração seja um inteiro
        try:
            duracao = int(request.form.get('duracao')) 
        except ValueError:
            flash('Duração deve ser um número inteiro.', 'danger')
            return redirect(url_for('admin_bp.new_service'))

        if nome and duracao:
            # Validação: Checar se o nome já existe (RNF05: Integridade de Dados)
            if Service.query.filter_by(nome=nome).first():
                flash('Um serviço com este nome já existe.', 'warning')
                return redirect(url_for('admin_bp.new_service'))

            new_service = Service(
                nome=nome,
                descricao=descricao,
                duracao=duracao
            )
            new_service.save()
            flash(f'Serviço "{nome}" criado com sucesso!', 'success')
            return redirect(url_for('admin_bp.manage_services'))
        
        flash('Nome e Duração são obrigatórios.', 'danger')

    # Para GET
    return render_template('admin/service_form.html', service=None)



@admin_bp.route('/services/edit/<int:service_id>', methods=['GET', 'POST'])
@admin_required
def edit_service(service_id):
    """RF03 - Edita um serviço existente."""
    service = Service.query.get_or_404(service_id)
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        descricao = request.form.get('descricao')
        
        try:
            duracao = int(request.form.get('duracao'))
        except ValueError:
            flash('Duração deve ser um número inteiro.', 'danger')
            return redirect(url_for('admin_bp.edit_service', service_id=service_id))

        if nome and duracao:
            # Validação de nome duplicado, exceto para o serviço atual
            existing_service = Service.query.filter(
                Service.nome == nome,
                Service.id != service_id
            ).first()
            
            if existing_service:
                flash('Outro serviço com este nome já existe.', 'warning')
                return redirect(url_for('admin_bp.edit_service', service_id=service_id))
            
            service.nome = nome
            service.descricao = descricao
            service.duracao = duracao
            service.save()
            flash(f'Serviço "{nome}" atualizado com sucesso!', 'success')
            return redirect(url_for('admin_bp.manage_services'))
            
        flash('Nome e Duração são obrigatórios.', 'danger')

    # Para GET
    return render_template('admin/service_form.html', service=service)


@admin_bp.route('/services/delete/<int:service_id>', methods=['POST'])
@admin_required
def delete_service(service_id):
    """RF03 - Exclui um serviço."""
    service = Service.query.get_or_404(service_id)
    nome = service.nome
    
    # Adicionar lógica de verificação de agendamentos futuros aqui (RNF05: Integridade)
    
    service.delete()
    flash(f'Serviço "{nome}" excluído permanentemente.', 'warning')
    return redirect(url_for('admin_bp.manage_services'))



# -------------------------------------------------------------
# ROTAS DE HORÁRIOS (CRUD - RF04)
# -------------------------------------------------------------

@admin_bp.route('/schedules')
@admin_required
def manage_schedules():
    """RF04 - Exibe a lista de todos os horários cadastrados."""
    # Ordena por dia da semana e hora de início para melhor visualização
    schedules = Schedule.query.order_by(Schedule.dia_semana, Schedule.hora_inicio).all()
    
    # Mapeamento de números para nomes de dias da semana para exibição no template
    dias_semana_map = {
        0: 'Segunda-feira', 1: 'Terça-feira', 2: 'Quarta-feira', 
        3: 'Quinta-feira', 4: 'Sexta-feira', 5: 'Sábado', 6: 'Domingo'
    }
    
    return render_template('admin/schedules.html', 
                           schedules=schedules, 
                           dias_semana_map=dias_semana_map)

@admin_bp.route('/schedules/new', methods=['GET', 'POST'])
@admin_required
def new_schedule():
    """RF04 - Cria um novo horário."""
    dias_semana_map = {
        0: 'Segunda-feira', 1: 'Terça-feira', 2: 'Quarta-feira', 
        3: 'Quinta-feira', 4: 'Sexta-feira', 5: 'Sábado', 6: 'Domingo'
    }
    
    if request.method == 'POST':
        dia_semana = request.form.get('dia_semana', type=int) # 0=Seg, 6=Dom
        hora_inicio = request.form.get('hora_inicio') # Ex: "09:00"
        hora_fim = request.form.get('hora_fim')       # Ex: "18:00"
        
        # 1. Validação de Conflito de Horário (RNF05: Integridade)
        # Verifica se já existe um bloco para o mesmo dia que se sobrepõe
        # Esta é uma validação simplificada e idealmente deveria ser mais robusta em um projeto final.
        existing_schedule = Schedule.query.filter(
            Schedule.dia_semana == dia_semana,
            Schedule.hora_inicio < hora_fim, # O início do novo bloco é antes do fim do existente
            Schedule.hora_fim > hora_inicio # O fim do novo bloco é depois do início do existente
        ).first()

        if existing_schedule:
            flash(f'Conflito de horário! Já existe um bloco cadastrado para {dias_semana_map.get(dia_semana)} que se sobrepõe.', 'danger')
            return redirect(url_for('admin_bp.new_schedule'))

        new_schedule = Schedule(
            dia_semana=dia_semana,
            hora_inicio=hora_inicio,
            hora_fim=hora_fim
        )
        new_schedule.save()
        flash(f'Horário de {hora_inicio} às {hora_fim} em {dias_semana_map.get(dia_semana)} criado com sucesso!', 'success')
        return redirect(url_for('admin_bp.manage_schedules'))

    # Para GET
    return render_template('admin/schedule_form.html', 
                           schedule=None, 
                           dias_semana_map=dias_semana_map)


@admin_bp.route('/schedules/delete/<int:schedule_id>', methods=['POST'])
@admin_required
def delete_schedule(schedule_id):
    """RF04 - Exclui um bloco de horário."""
    schedule = Schedule.query.get_or_404(schedule_id)
    
    # RNF05 - Integridade: Verificar se há agendamentos vinculados a este horário
    # Se houver, a exclusão seria bloqueada ou os agendamentos teriam que ser cancelados
    
    schedule.delete()
    flash('Bloco de horário excluído permanentemente.', 'warning')
    return redirect(url_for('admin_bp.manage_schedules'))


# app/blueprints/admin/routes.py

# ... imports dos modelos Booking e User aqui ...

@admin_bp.route('/bookings')
@login_required
@admin_required
def manage_bookings():
    # 🚨 CORREÇÃO: Descomente e execute a query:
    agendamentos = Booking.query.order_by(Booking.data_agendamento.desc()).all() 
    
    # 2. Renderize o template
    return render_template('admin/manage_bookings.html', 
                           agendamentos=agendamentos, 
                           active_page='admin.manage_bookings')

# ...

@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    # 🚨 CORREÇÃO: Descomente e execute a query:
    users = User.query.order_by(User.nome).all() 
    
    # 2. Renderize o template
    return render_template('admin/manage_users.html', 
                           users=users, 
                           active_page='admin.manage_users')


# app/blueprints/admin/routes.py

# ... imports ...

@admin_bp.route('/users/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_user():
    # user = None # Usado para indicar que é um novo cadastro
    
    if request.method == 'POST':
        # LÓGICA DE CRIAÇÃO DO NOVO USUÁRIO:
        # 1. Obter dados do formulário (nome, email, senha, is_admin, is_active)
        # 2. Validar dados (emails, senhas)
        # 3. Criar e salvar o novo objeto User no banco de dados
        # 4. Exibir flash message de sucesso
        return redirect(url_for('admin.manage_users'))

    # Método GET: Exibir o formulário vazio
    # Passamos 'user=None' para o template saber que é um novo cadastro
    return render_template('admin/user_form.html', user=None, active_page='admin.manage_users')

# app/blueprints/admin/routes.py

@admin_bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Permite ao administrador editar os dados de um usuário."""
    
    # 1. Obter o usuário existente ou retornar 404
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        # 2. Processar a submissão do formulário
        
        # Coletar dados (Nome e Email são obrigatórios)
        nome = request.form.get('nome')
        email = request.form.get('email')
        
        # Coletar checkboxes (Retornam 'on' se checado, ou None se não checado)
        # O valor booleano é usado para decidir o perfil/status
        is_admin_check = request.form.get('is_admin')
        is_active_check = request.form.get('is_active') 
        
        # Converte o valor do formulário para booleano (True se 'on', False se None)
        is_admin = is_admin_check is not None
        is_active = is_active_check is not None
        
        if nome and email:
            # 3. Validação de Email Duplicado (exceto para o usuário atual)
            existing_email = User.query.filter(
                User.email == email,
                User.id != user_id
            ).first()
            
            if existing_email:
                flash('Este e-mail já está sendo usado por outro usuário.', 'danger')
                return redirect(url_for('admin.edit_user', user_id=user_id))
            
            # 4. Atualizar os campos
            user.nome = nome
            user.email = email
            
            # 🚨 CORREÇÃO PRINCIPAL DO ERRO 'AttributeError':
            # Em vez de user.is_admin = is_admin, alteramos o campo PERFIL
            if is_admin:
                user.perfil = 'Administrador'
            else:
                user.perfil = 'Cliente'
            
            # Se você usa o campo 'is_active' no modelo, atualize-o
            # (Assumindo que você adicionou is_active no modelo User)
            user.is_active = is_active 
            
            # 5. Salvar (Assumindo que user.save() ou db.session.commit() é chamado)
            user.save() 
            
            flash(f'Usuário "{nome}" atualizado com sucesso!', 'success')
            return redirect(url_for('admin.manage_users'))
        
        flash('Nome e E-mail são campos obrigatórios.', 'danger')

    # 6. Retorno para o método GET (Exibir o formulário pré-preenchido)
    return render_template('admin/user_form.html', user=user, active_page='admin.manage_users')

@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Exclui um usuário (requer POST)."""
    
    # 1. Encontrar o usuário. Se não existir, retorna 404.
    user = User.query.get_or_404(user_id)
    nome_usuario = user.nome # Armazena o nome antes de deletar
    
    # 2. RNF (Regra Não Funcional) de Segurança: Impedir a exclusão do último administrador
    #    (Assumindo que você precisa de pelo menos um admin no sistema)
    if user.is_admin:
        total_admins = User.query.filter_by(is_admin=True).count()
        if total_admins == 1:
            flash('Não é possível excluir o único administrador do sistema.', 'danger')
            return redirect(url_for('admin.manage_users'))
    
    # 3. Excluir o usuário do banco de dados (Assumindo que user.delete() executa o commit)
    try:
        user.delete() 
        flash(f'Usuário "{nome_usuario}" excluído permanentemente.', 'success')
    except Exception as e:
        # Lidar com erros de integridade (ex: chaves estrangeiras, se o DB impedir)
        flash(f'Erro ao excluir usuário: {str(e)}', 'danger')
        # Se for necessário, pode-se fazer um rollback aqui: db.session.rollback()
    
    return redirect(url_for('admin.manage_users'))


# app/blueprints/admin/routes.py

# ... (Continuação das rotas administrativas) ...

@admin_bp.route('/bookings/confirm/<int:booking_id>', methods=['POST'])
@login_required
@admin_required
def confirm_booking(booking_id):
    """Altera o status do agendamento para 'Confirmado'."""
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.status == 'Pendente':
        booking.status = 'Confirmado'
        # Assumindo que booking.save() executa o commit no DB
        booking.save() 
        flash(f'Agendamento de {booking.servico.nome} em {booking.data_agendamento.strftime("%d/%m/%Y")} CONFIRMADO com sucesso!', 'success')
    else:
        flash('O agendamento não pode ser confirmado.', 'warning')
        
    return redirect(url_for('admin.manage_bookings'))


@admin_bp.route('/bookings/cancel/<int:booking_id>', methods=['POST'])
@login_required
@admin_required
def cancel_booking(booking_id):
    """Altera o status do agendamento para 'Cancelado'."""
    booking = Booking.query.get_or_404(booking_id)
    
    # RNF: Se o agendamento já passou, talvez você queira impedir o cancelamento (ou mudar para 'Concluído').
    
    if booking.status != 'Cancelado':
        booking.status = 'Cancelado'
        # Assumindo que booking.save() executa o commit no DB
        booking.save()
        flash(f'Agendamento de {booking.servico.nome} em {booking.data_agendamento.strftime("%d/%m/%Y")} CANCELADO.', 'warning')
    else:
        flash('O agendamento já estava cancelado.', 'info')
        
    return redirect(url_for('admin.manage_bookings'))