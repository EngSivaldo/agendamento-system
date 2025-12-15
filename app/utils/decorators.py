# app/utils/decorators.py

from functools import wraps
from flask import redirect, url_for, flash # Removi o 'abort' para usar flash/redirect
from flask_login import current_user

def role_required(role):
    """Decorator para restringir acesso baseado no perfil do usuário (RF02)."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 1. Checa autenticação (Apesar de ser bom ter, é redundante se usar @login_required)
            if not current_user.is_authenticated:
                # CORREÇÃO DE NOMENCLATURA: Use 'auth.login'
                return redirect(url_for('auth.login')) 
                
            # 2. Checa perfil
            if current_user.perfil != role:
                flash("Acesso não autorizado. Seu perfil não permite esta ação.", 'danger')
                # CORREÇÃO DE NOMENCLATURA: Use 'client.index'
                return redirect(url_for('client.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# A função 'admin_required' DEVE vir depois de 'role_required'
def admin_required(f):
    """Alias para role_required('Administrador')"""
    return role_required('Administrador')(f)