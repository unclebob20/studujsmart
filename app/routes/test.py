from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user

test_bp = Blueprint('test', __name__)


@test_bp.route('/quick/<int:subject_id>')
@login_required
def quick_test(subject_id):
    """Start a quick test"""
    # TODO: Implement in Week 2
    return render_template('test/quick.html', subject_id=subject_id)


@test_bp.route('/<int:session_id>')
@login_required
def take_test(session_id):
    """Take test interface"""
    # TODO: Implement in Week 2
    return render_template('test/take.html', session_id=session_id)


@test_bp.route('/<int:session_id>/results')
@login_required
def results(session_id):
    """View test results"""
    # TODO: Implement in Week 3
    return render_template('test/results.html', session_id=session_id)