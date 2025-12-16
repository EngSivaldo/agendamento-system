# app/models/user.py

from app import db  # CORREÇÃO: Importa o objeto 'db' globalmente
from app.models.base import BaseMixin
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.booking import Booking  # Verifique se está correto o caminho de importação

class User(db.Model, UserMixin, BaseMixin):
    __tablename__ = 'usuario'
    
    # ==========================================================
    # CAMPOS
    # ==========================================================
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    perfil = db.Column(db.String(50), default='Cliente', nullable=False)  # Administrador/Cliente
    is_active = db.Column(db.Boolean, default=True)  # Coluna do Flask-Login
    
    # ==========================================================
    # RELACIONAMENTO COM AGENDAMENTOS
    # ==========================================================
    agendamentos = db.relationship(
        'Booking',
        foreign_keys='Booking.user_id',
        back_populates='user',
        lazy='dynamic'
    )

    # ==========================================================
    # MÉTODOS DE SEGURANÇA (Funções de senha)
    # ==========================================================
    def set_password(self, senha):
        """Seta a senha após gerar um hash seguro"""
        if senha:
            self.senha_hash = generate_password_hash(senha)
        else:
            raise ValueError("A senha não pode ser vazia.")

    def check_password(self, senha):
        """Verifica se a senha fornecida é válida"""
        return check_password_hash(self.senha_hash, senha)

    @property
    def is_admin(self):
        """Verifica se o usuário é um administrador"""
        return self.perfil == 'Administrador'
    
    def __repr__(self):
        """Representação do usuário"""
        return f'<User {self.email} ({self.perfil})>'

# ==========================================================
# COMANDO CLI (Criação do Administrador)
# ==========================================================
def register_cli_commands(app):
    import click
    
    @app.cli.command("create-admin")
    @click.option('--email', default='admin@sistema.com', help='Email do administrador.')
    @click.option('--password', default='123456', help='Senha do administrador.')
    def create_admin(email, password):
        """Criação do administrador com dados iniciais"""
        # Verifica se o administrador já existe
        if User.query.filter_by(email=email).first():
            click.echo(f"Administrador com email {email} já existe.")
            return

        # Criação do novo administrador
        admin = User(
            nome='Administrador Principal',
            email=email,
            perfil='Administrador',
            is_active=True
        )
        admin.set_password(password)
        
        # Adiciona o novo administrador no banco de dados
        db.session.add(admin)
        db.session.commit()
        click.echo(f"Administrador ({email}) criado com sucesso!")
