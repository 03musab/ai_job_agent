from functools import wraps
from flask import flash, redirect, url_for, jsonify, request
from flask_login import current_user


def require_role(role: str):
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


def require_company_owner(f):
    """
    Decorator for company routes that require the authenticated recruiter
    to own the resource. Must be used together with @login_required and
    @require_role('recruiter'). The route must accept a recruiter_id parameter.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        recruiter_id = kwargs.get('recruiter_id')
        if recruiter_id is None:
            return jsonify({'success': False, 'message': 'Invalid request.'}), 400
        if recruiter_id != current_user.id:
            return jsonify({'success': False, 'message': 'Access denied. You can only manage your own company.'}), 403
        return f(*args, **kwargs)
    return decorated_function
