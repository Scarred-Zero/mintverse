from flask import redirect, url_for, flash
from flask_login import current_user
from functools import wraps


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if (
            not current_user.is_authenticated
            or getattr(current_user, "role", None) != "admin"
        ):
            flash("Admin access required.", "danger")
            return redirect(url_for("admin.admin_login_page"))
        return f(*args, **kwargs)

    return decorated_function
