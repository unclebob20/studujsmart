from flask import Blueprint, render_template
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func
from app import db
from app.models.subject import Subject, UserTopicProgress, Topic
from app.models.test import TestSession
from app.models.gamification import UserBadge

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    """Main dashboard"""

    # Get user's subjects
    user_subjects = [us.subject_id for us in current_user.user_subjects if us.is_active]
    subjects = Subject.query.filter(Subject.id.in_(user_subjects)).all() if user_subjects else []

    # Calculate XP progress
    xp_thresholds = [0, 100, 250, 500, 1000, 2000, 4000, 7000, 11000, 16000]
    current_threshold = xp_thresholds[current_user.level - 1] if current_user.level <= len(xp_thresholds) else 0
    next_threshold = xp_thresholds[current_user.level] if current_user.level < len(
        xp_thresholds) else current_threshold + 5000
    xp_to_next_level = next_threshold - current_user.xp
    xp_progress = ((current_user.xp - current_threshold) / (
                next_threshold - current_threshold)) * 100 if next_threshold > current_threshold else 100

    # Get test statistics
    tests_completed = TestSession.query.filter_by(
        user_id=current_user.id,
        status='completed'
    ).count()

    week_ago = datetime.utcnow() - timedelta(days=7)
    tests_this_week = TestSession.query.filter(
        TestSession.user_id == current_user.id,
        TestSession.status == 'completed',
        TestSession.completed_at >= week_ago
    ).count()

    # Calculate average accuracy
    avg_result = db.session.query(
        func.avg(TestSession.percentage)
    ).filter(
        TestSession.user_id == current_user.id,
        TestSession.status == 'completed'
    ).scalar()

    avg_accuracy = round(avg_result or 0, 1)

    # Get progress for each subject
    progress_data = {}
    for subject in subjects:
        topic_progress = UserTopicProgress.query.join(Topic).filter(
            UserTopicProgress.user_id == current_user.id,
            Topic.subject_id == subject.id
        ).all()

        if topic_progress:
            avg_acc = sum(tp.accuracy_rate for tp in topic_progress) / len(topic_progress)
            progress_data[subject.id] = {
                'accuracy': round(avg_acc, 1),
                'topics_count': len(topic_progress)
            }
        else:
            progress_data[subject.id] = {'accuracy': 0, 'topics_count': 0}

    # Get weak topics (accuracy < 60%)
    weak_topics = db.session.query(
        UserTopicProgress, Topic
    ).join(Topic).filter(
        UserTopicProgress.user_id == current_user.id,
        UserTopicProgress.accuracy_rate < 60
    ).order_by(UserTopicProgress.accuracy_rate.asc()).limit(3).all()

    weak_topics_data = [{
        'id': topic.id,
        'name_sk': topic.name_sk,
        'accuracy': round(progress.accuracy_rate, 1)
    } for progress, topic in weak_topics]

    # Get recent badges
    recent_badges = UserBadge.query.filter_by(
        user_id=current_user.id
    ).order_by(UserBadge.earned_at.desc()).limit(5).all()

    # Get recent tests
    recent_tests = TestSession.query.filter_by(
        user_id=current_user.id,
        status='completed'
    ).order_by(TestSession.completed_at.desc()).limit(5).all()

    return render_template(
        'dashboard/index.html',
        subjects=subjects,
        progress_data=progress_data,
        xp_to_next_level=xp_to_next_level,
        xp_progress=round(xp_progress, 1),
        tests_completed=tests_completed,
        tests_this_week=tests_this_week,
        avg_accuracy=avg_accuracy,
        weak_topics=weak_topics_data,
        recent_badges=recent_badges,
        recent_tests=recent_tests
    )
