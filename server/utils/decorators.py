from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user


def admin_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            flash("Access denied: Admins only.", "danger")
            return redirect(url_for("user.dashboard_page"))  # Redirect non-admins
        return func(*args, **kwargs)

    return decorated_function
