# app/models/base.py (SOLUÇÃO CORRIGIDA PARA ACESSO À INSTÂNCIA GLOBAL)

from flask import current_app
# Removida a importação de flask_sqlalchemy, que causou o erro.

class BaseMixin:
    """Mixin com métodos comuns de persistência."""
    
    def _get_db_session(self):
        """
        Retorna a sessão do banco de dados (db.session) 
        importando a instância 'db' de forma segura.
        """
        # A importação LOCAL é segura agora que __init__.py foi corrigido.
        # Isso garante que a instância 'db' seja a ÚNICA já registrada.
        from app import db # Importa a instância 'db' que foi definida globalmente em app/__init__.py
        return db

    def save(self):
        """Salva a instância no banco de dados."""
        db_instance = self._get_db_session()
        try:
            db_instance.session.add(self)
            db_instance.session.commit()
        except Exception as e:
            db_instance.session.rollback()
            current_app.logger.error(f"Erro ao salvar objeto: {e}")
            raise e

    def delete(self):
        """Remove a instância do banco de dados."""
        db_instance = self._get_db_session()
        try:
            db_instance.session.delete(self)
            db_instance.session.commit()
        except Exception as e:
            db_instance.session.rollback()
            current_app.logger.error(f"Erro ao deletar objeto: {e}")
            raise e