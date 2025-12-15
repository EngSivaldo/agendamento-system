# app/services/booking_service.py
from app.models.booking import Booking
from app.services.availability_service import AvailabilityService
from app.extensions.database import db

class BookingConflictError(Exception):
    pass

class BookingService:
    @staticmethod
    def create_booking(user_id, service_id, schedule_id):
        # RF05, RF06 - Lógica de Criação e Transação
        
        # 1. Validação de Conflito usando o AvailabilityService
        # ... lógica de verificação ...
        
        # 2. Criação
        # ... new_booking.save() ...
        pass
        
    @staticmethod
    def get_user_bookings(user_id):
        return Booking.query.filter_by(user_id=user_id).all()