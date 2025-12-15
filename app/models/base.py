# app/models/base.py
from app.extensions.database import db

class BaseMixin:
    """Mixin com métodos comuns de persistência (Implícito Repository Pattern)."""
    
    def save(self):
        """Salva a instância no banco de dados."""
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e # Re-lança a exceção para que o Service Layer possa tratá-la

    def delete(self):
        """Remove a instância do banco de dados."""
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e