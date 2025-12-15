# app/utils/decorators.py
from functools import wraps
from flask import abort, redirect, url_for, flash
from flask_login import current_user

def role_required(role):
    """Decorator para restringir acesso baseado no perfil do usuário (RF02)."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth_bp.login'))
            if current_user.perfil != role:
                flash("Acesso não autorizado. Seu perfil não permite esta ação.", 'danger')
                return redirect(url_for('client_bp.index')) # Redireciona para home do cliente
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Alias para role_required('Administrador')"""
    return role_required('Administrador')(f)