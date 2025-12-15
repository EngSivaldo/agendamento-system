# app/models/schedule.py (CORRETO E FINAL)

from app import db # CORREÇÃO: Assegurando que a importação do db é consistente
from app.models.base import BaseMixin

class Schedule(db.Model, BaseMixin):
    __tablename__ = 'schedule'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # 0=Segunda, 6=Domingo
    dia_semana = db.Column(db.Integer, nullable=False) 
    
    hora_inicio = db.Column(db.String(5), nullable=False) # Ex: "09:00"
    hora_fim = db.Column(db.String(5), nullable=False)  # Ex: "18:00"
    
    # NOTA: O db.relationship foi removido daqui!
    
    def __repr__(self):
        return f'<Schedule {self.dia_semana} {self.hora_inicio}-{self.hora_fim}>'

# =============================================================
# DEFINIÇÃO TARDIA DO RELACIONAMENTO (APÓS A CLASSE)
# ISSO QUEBRA O CICLO DE DEPENDÊNCIA DO SQLALCHEMY
# =============================================================

# 1. Relação com Booking (RESOLVE O ÚLTIMO ERRO)
Schedule.agendamentos = db.relationship(
    'Booking', 
    back_populates='schedule_slot', 
    lazy=True
)