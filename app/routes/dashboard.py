from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.subject import Subject, UserTopicProgress

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    """Main dashboard"""
    # Get user's subjects
    user_subjects = [us.subject_id for us in current_user.user_subjects if us.is_active]
    subjects = Subject.query.filter(Subject.id.in_(user_subjects)).all() if user_subjects else []

    # Get progress for each subject
    progress_data = {}
    for subject in subjects:
        topic_progress = UserTopicProgress.query.join(
            Topic
        ).filter(
            UserTopicProgress.user_id == current_user.id,
            Topic.subject_id == subject.id
        ).all()

        if topic_progress:
            avg_accuracy = sum(tp.accuracy_rate for tp in topic_progress) / len(topic_progress)
            progress_data[subject.id] = {
                'accuracy': round(avg_accuracy, 1),
                'topics_count': len(topic_progress)
            }
        else:
            progress_data[subject.id] = {'accuracy': 0, 'topics_count': 0}

    return render_template(
        'dashboard/index.html',
        subjects=subjects,
        progress_data=progress_data
    )