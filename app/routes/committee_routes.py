from flask import Blueprint, render_template
from flask_login import login_required, current_user

committee_bp = Blueprint('committee', __name__, template_folder='templates/committee')

@committee_bp.route('/dashboard')
@login_required
def dashboard():
    return "<h2>Scholarship Committee Dashboard (Coming Soon)</h2>"
