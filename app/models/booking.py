# app/models/booking.py (CORRETO E FINAL - COM DATETIME)

from app import db 
from app.models.base import BaseMixin

class Booking(db.Model, BaseMixin):
    __tablename__ = 'agendamento'
    
    id = db.Column(db.Integer, primary_key=True)
    # 🚨 TROCA EFETUADA: Agora armazena Data E Hora
    data_agendamento = db.Column('data', db.DateTime, nullable=False) 
    
    status = db.Column(db.String(50), default='Pendente', nullable=False)
    
    # Chaves Estrangeiras
    user_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('servico.id'), nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'), nullable=False)
    
    def confirm(self):
        self.status = 'Confirmado'
        self.save()

    def cancel(self):
        self.status = 'Cancelado'
        self.save()

# =============================================================
# DEFINIÇÃO TARDIA DE TODOS OS RELACIONAMENTOS
# =============================================================

# 1. Relação com User (CORREÇÃO AQUI: Mudança de 'cliente' para 'user')
# Esta correção alinha o modelo com o que o template admin/manage_bookings.html espera.
Booking.user = db.relationship( 
    'User', 
    back_populates='agendamentos'
)

# 2. Relação com Service
Booking.servico = db.relationship(
    'Service', 
    back_populates='agendamentos'
)

# 3. Relação com Schedule
Booking.schedule_slot = db.relationship(
    'Schedule', 
    back_populates='agendamentos'
)