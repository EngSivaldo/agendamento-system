# app/blueprints/auth/routes.py (Versão Consolidada e Corrigida)

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user 
from app.models.user import User
from flask import current_app
from app import db

from app import db # Objeto DB para operações de sessão (necessário para o .save() customizado)

# -------------------------------------------------------------
# DEFINIÇÃO DO BLUEPRINT
# -------------------------------------------------------------
auth_bp = Blueprint('auth', __name__) 

# =============================================================
# ROTAS DE AUTENTICAÇÃO (RF01, RF02)
# =============================================================

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """RF01 - Rota de Login."""

    if current_user.is_authenticated:
        if current_user.perfil == 'Administrador':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('client.index'))

    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        try:
            # ✅ CONSULTA SIMPLES, SEM no_autoflush
            user = db.session.query(User).filter_by(email=email).first()
        except Exception as e:
            current_app.logger.error(f"Erro no login: {e}")
            flash('Erro interno ao acessar o banco de dados. Tente novamente.', 'danger')
            return render_template('auth/login.html')

        if user and user.check_password(senha):
            login_user(user)
            flash(f'Bem-vindo(a), {user.nome}!', 'success')

            if user.perfil == 'Administrador':
                return redirect(url_for('admin.dashboard'))

            next_page = request.args.get('next')
            return redirect(next_page or url_for('client.index'))

        flash('Email ou senha inválidos.', 'danger')

    return render_template('auth/login.html')



@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """RF01 - Rota de Cadastro de novo usuário (Perfil Cliente)."""
    if current_user.is_authenticated:
        # Redireciona para o dashboard apropriado se já estiver logado
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
            return redirect(url_for('auth.register'))

        # 1. Validação de Email existente
        if User.query.filter_by(email=email).first():
            flash('Este email já está cadastrado.', 'warning')
            return redirect(url_for('auth.register'))

        # 2. Criação do Usuário
        new_user = User(
            nome=nome,
            email=email,
            perfil='Cliente' 
        )
        new_user.set_password(senha)
        
        # 3. Salvamento no DB
        try:
            # Assumindo que new_user.save() existe e faz o commit
            new_user.save() 
        except AttributeError:
            # Fallback para SQLAlchemy padrão se o método save não existir
            db.session.add(new_user)
            db.session.commit()

        flash('Cadastro realizado com sucesso! Faça login para continuar.', 'success')
        return redirect(url_for('auth.login'))

    # Para GET
    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Rota de Logout."""
    logout_user()
    flash('Você foi desconectado(a).', 'info')
    # Redireciona para o login após o logout
    return redirect(url_for('auth.login'))


