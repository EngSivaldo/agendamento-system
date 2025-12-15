# app/models/booking.py (CORRETO E FINAL)

from app import db # Importação do db corrigida
from app.models.base import BaseMixin

class Booking(db.Model, BaseMixin):
    __tablename__ = 'agendamento'
    
    id = db.Column(db.Integer, primary_key=True)
    data_agendamento = db.Column('data', db.Date, nullable=False)
    
    status = db.Column(db.String(50), default='Pendente', nullable=False)
    
    # Chaves Estrangeiras
    user_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('servico.id'), nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'), nullable=False)
    
    # IMPORTANTE: Nenhum db.relationship está definido aqui dentro.
    
    def confirm(self):
        self.status = 'Confirmado'
        self.save()

    def cancel(self):
        self.status = 'Cancelado'
        self.save()

# =============================================================
# DEFINIÇÃO TARDIA DE TODOS OS RELACIONAMENTOS (APÓS A CLASSE)
# ISSO QUEBRA O CICLO DE DEPENDÊNCIA DO SQLALCHEMY
# =============================================================

# 1. Relação com User
Booking.cliente = db.relationship(
    'User', 
    back_populates='agendamentos'
)

# 2. Relação com Service (RESOLVE O ERRO ATUAL)
Booking.servico = db.relationship(
    'Service', 
    back_populates='agendamentos'
)

# 3. Relação com Schedule (Previne um erro futuro)
Booking.schedule_slot = db.relationship(
    'Schedule', 
    back_populates='agendamentos'
)