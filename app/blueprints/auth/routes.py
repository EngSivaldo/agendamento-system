from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_user, logout_user, login_required, current_user 
from app.models.user import User
from app import db # Importa a instância do SQLAlchemy (ou sua variável db)

# -------------------------------------------------------------
# DEFINIÇÃO DO BLUEPRINT
# -------------------------------------------------------------
# O nome do Blueprint é 'auth'. O prefixo '/auth' será definido
# no app/__init__.py ao registrar.
auth_bp = Blueprint('auth', __name__) 

# =============================================================
# 1. ROTAS DE AUTENTICAÇÃO PRINCIPAIS
# =============================================================

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Endpoint: 'auth.login' (URL: /auth/login)
    Lida com o formulário de login e autenticação do usuário.
    """
    
    # Se o usuário já estiver autenticado, redireciona
    if current_user.is_authenticated:
        if current_user.perfil == 'Administrador':
            # Assumindo que a rota 'admin.dashboard' existe
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('client.index'))

    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        try:
            user = db.session.query(User).filter_by(email=email).first()
        except Exception as e:
            current_app.logger.error(f"Erro no login: {e}")
            flash('Erro interno ao acessar o banco de dados. Tente novamente.', 'danger')
            return render_template('auth/login.html')

        if user and user.check_password(senha):
            login_user(user)
            flash(f'Bem-vindo(a), {user.nome.split()[0]}!', 'success')

            if user.perfil == 'Administrador':
                return redirect(url_for('admin.dashboard'))

            # Redireciona para a página 'next' (se houver) ou para o index do cliente
            next_page = request.args.get('next')
            return redirect(next_page or url_for('client.index'))

        flash('Email ou senha inválidos.', 'danger')

    return render_template('auth/login.html', title='Login')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Endpoint: 'auth.register' (URL: /auth/register)
    Lida com o cadastro de novos usuários com perfil 'Cliente'.
    """
    if current_user.is_authenticated:
        if current_user.perfil == 'Administrador':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('client.index'))

    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        confirm_senha = request.form.get('confirm_senha')

        if senha != confirm_senha:
            flash('As senhas não coincidem.', 'danger')
            return render_template('auth/register.html', nome=nome, email=email) # Mantém os dados preenchidos

        # 1. Validação de Email existente
        if User.query.filter_by(email=email).first():
            flash('Este email já está cadastrado.', 'warning')
            return render_template('auth/register.html', nome=nome)

        # 2. Criação do Usuário
        new_user = User(
            nome=nome,
            email=email,
            perfil='Cliente' 
        )
        new_user.set_password(senha)
        
        # 3. Salvamento no DB
        try:
            # Assumindo que o método .save() está definido no seu modelo User
            # Se não estiver definido, use: db.session.add(new_user); db.session.commit()
            if hasattr(new_user, 'save'):
                new_user.save()
            else:
                 db.session.add(new_user)
                 db.session.commit()
                 
            flash('Cadastro realizado com sucesso! Faça login para continuar.', 'success')
            return redirect(url_for('auth.login'))
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erro ao cadastrar usuário: {e}")
            flash('Erro ao processar o cadastro. Tente novamente.', 'danger')

    return render_template('auth/register.html', title='Cadastro')


@auth_bp.route('/logout')
@login_required
def logout():
    """Endpoint: 'auth.logout' (URL: /auth/logout)
    Desconecta o usuário.
    """
    logout_user()
    flash('Você foi desconectado(a).', 'info')
    return redirect(url_for('auth.login'))


# =============================================================
# 2. ROTAS DE GERENCIAMENTO DE CONTA
# =============================================================

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Endpoint: 'auth.change_password' (URL: /auth/change-password)
    Permite ao usuário logado alterar sua senha.
    """
    
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not current_user.check_password(current_password):
            flash('A Senha Atual informada está incorreta.', 'danger')
        elif new_password != confirm_password:
            flash('A Nova Senha e a Confirmação de Senha não coincidem.', 'danger')
        else:
            try:
                # 1. Atualiza a senha no objeto current_user
                current_user.set_password(new_password)
                
                # 2. Salva no banco de dados
                if hasattr(current_user, 'save'):
                    current_user.save()
                else:
                    db.session.add(current_user)
                    db.session.commit()
                    
                flash('Senha alterada com sucesso!', 'success')
                # Redireciona de volta para o perfil
                return redirect(url_for('client.my_profile'))
                
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Erro ao alterar senha: {e}")
                flash('Erro interno ao salvar a nova senha.', 'danger')
    
    # Retorna o template de alteração de senha
    return render_template('auth/change_password.html', 
                           title='Alterar Senha')