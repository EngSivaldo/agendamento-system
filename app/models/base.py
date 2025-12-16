from flask import current_app
from datetime import datetime

class BaseMixin:
    """Mixin com métodos comuns de persistência e soft delete."""

    # 🔥 COLUNAS PADRÃO
    created_at = None
    updated_at = None
    deleted_at = None

    def _get_db_session(self):
        """
        Retorna a sessão do banco de dados (db.session)
        usando a instância global registrada no app.
        """
        from app import db
        return db

    def save(self):
        """Salva ou atualiza a instância no banco."""
        db_instance = self._get_db_session()
        try:
            if hasattr(self, 'updated_at'):
                self.updated_at = datetime.utcnow()

            db_instance.session.add(self)
            db_instance.session.commit()
        except Exception as e:
            db_instance.session.rollback()
            current_app.logger.error(f"Erro ao salvar objeto: {e}")
            raise

    def soft_delete(self):
        """Soft delete (não remove fisicamente)."""
        db_instance = self._get_db_session()
        try:
            self.deleted_at = datetime.utcnow()
            db_instance.session.commit()
        except Exception as e:
            db_instance.session.rollback()
            current_app.logger.error(f"Erro ao soft delete: {e}")
            raise

    def restore(self):
        """Restaura um registro deletado."""
        db_instance = self._get_db_session()
        try:
            self.deleted_at = None
            db_instance.session.commit()
        except Exception as e:
            db_instance.session.rollback()
            current_app.logger.error(f"Erro ao restaurar objeto: {e}")
            raise

    def delete(self):
        """
        DELETE DEFINITIVO (USAR SOMENTE ADMIN)
        Mantido para compatibilidade.
        """
        db_instance = self._get_db_session()
        try:
            db_instance.session.delete(self)
            db_instance.session.commit()
        except Exception as e:
            db_instance.session.rollback()
            current_app.logger.error(f"Erro ao deletar objeto: {e}")
            raise
