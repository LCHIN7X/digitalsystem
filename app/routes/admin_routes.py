admin_bp = Blueprint('admin', __name__, template_folder='templates/admin')

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    total_apps = Application.query.count()
    total_scholarships = Scholarship.query.count()
    return render_template('dashboard.html', total_apps=total_apps, total_scholarships=total_scholarships)
