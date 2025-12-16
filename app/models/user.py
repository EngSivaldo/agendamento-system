# app/models/user.py

from app import db # CORREÇÃO: Importa o objeto 'db' globalmente
from app.models.base import BaseMixin
from flask_login import UserMixin 
from werkzeug.security import generate_password_hash, check_password_hash 
from app.models.booking import Booking # <--- ADICIONE ESTA LINHA
class User(db.Model, UserMixin, BaseMixin):
    __tablename__ = 'usuario'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    senha_hash = db.Column(db.String(255), nullable=False)
    perfil = db.Column(db.String(50), default='Cliente', nullable=False) # Administrador/Cliente

    # Coluna do Flask-Login
    is_active = db.Column(db.Boolean, default=True) 

    # NOTA: O db.relationship foi removido daqui!
    
    # Métodos de Segurança 
    def set_password(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_password(self, senha):
        return check_password_hash(self.senha_hash, senha)

    @property
    def is_admin(self):
        return self.perfil == 'Administrador'
    
    def __repr__(self):
        return f'<User {self.email} ({self.perfil})>'

# =============================================================
# DEFINIÇÃO TARDIA DO RELACIONAMENTO (Late Relationship Binding)
# CORREÇÃO DO ERRO InvalidRequestError
# =============================================================
User.agendamentos = db.relationship(
    'Booking', 
    back_populates='user', # 🚨 MUDANÇA AQUI: Era 'cliente', agora é 'user'
    lazy='dynamic'
)
# ---
# -------------------------------------------------------------
# COMANDO CLI 

def register_cli_commands(app):
    import click 
    
    @app.cli.command("create-admin")
    @click.option('--email', default='admin@sistema.com', help='Email do administrador.')
    @click.option('--password', default='123456', help='Senha do administrador.')
    def create_admin(email, password):
        if User.query.filter_by(email=email).first():
            click.echo(f"Administrador com email {email} já existe.")
            return

        admin = User(
            nome='Administrador Principal',
            email=email,
            perfil='Administrador',
            is_active=True 
        )
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        click.echo(f"Administrador ({email}) criado com sucesso!")