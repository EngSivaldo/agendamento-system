# app/services/availability_service.py
from app.models.schedule import Schedule
from app.extensions.database import db

class AvailabilityService:
    @staticmethod
    def get_available_schedules(service_id, desired_date=None):
        """RF04 - Retorna horários disponíveis para um serviço e opcionalmente uma data."""
        query = Schedule.query.filter_by(service_id=service_id, disponivel=True)
        if desired_date:
            query = query.filter_by(data=desired_date)

        return query.order_by(Schedule.data, Schedule.hora_inicio).all()

    @staticmethod
    def check_for_conflict(user_id, date, service_id):
        """Verifica se há conflito de agendamento para o usuário nesta data/serviço."""
        # Lógica de verificação de conflito mais complexa pode entrar aqui
        pass