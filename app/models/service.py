# app/models/service.py (CORRETO E FINAL)

from app import db # CORREÇÃO: Assegurando que a importação do db é consistente
from app.models.base import BaseMixin

class Service(db.Model, BaseMixin):
    __tablename__ = 'servico'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    descricao = db.Column(db.Text)
    duracao = db.Column(db.Integer, nullable=False) # Duração em minutos
    
    # IMPORTANTE: Os relacionamentos foram removidos daqui!
    
    # ... (métodos save, delete, etc.)

    # Se você tiver um __repr__
    def __repr__(self):
        return f'<Service {self.nome}>'

# =============================================================
# DEFINIÇÃO TARDIA DE TODOS OS RELACIONAMENTOS (APÓS A CLASSE)
# ISSO QUEBRA O CICLO DE DEPENDÊNCIA DO SQLALCHEMY
# =============================================================

# 1. Relação com Booking (RESOLVE O ERRO ATUAL)
Service.agendamentos = db.relationship(
    'Booking', 
    back_populates='servico', 
    lazy=True
)

# 2. Relacionamento com Schedule (Se ainda existir e se precisar de definição tardia)
# Se você removeu a FK, esta linha deve ser removida permanentemente, mas se 
# a intenção for manter o relacionamento muitos-para-muitos ou forçar um:
# Service.horarios = db.relationship('Schedule', backref='service', lazy=True)