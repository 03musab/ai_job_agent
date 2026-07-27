from functools import wraps
from flask import flash, redirect, url_for, jsonify, request
from flask_login import current_user

def require_role(role):
    """
    Decorator to restrict route access by user role.
    If the current user is not authenticated or does not have the required role,
    it returns a 403 Forbidden for API routes or redirects to the dashboard
    with a flash message for regular routes.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                if request.path.startswith('/api/'):
                    return jsonify({'error': 'Access denied. Insufficient permissions.'}), 403
                flash('Access denied. You do not have permission to view this page.', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator