from flask import Blueprint, jsonify
from flask_login import login_required, current_user

api_bp = Blueprint('api', __name__)


@api_bp.route('/subjects')
@login_required
def get_subjects():
    """Get all subjects"""
    from app.models.subject import Subject
    subjects = Subject.query.filter_by(is_active=True).all()

    return jsonify([{
        'id': s.id,
        'name': s.name_sk,
        'slug': s.slug,
        'icon': s.icon,
        'color': s.color
    } for s in subjects])


@api_bp.route('/subjects/<int:subject_id>/topics')
@login_required
def get_topics(subject_id):
    """Get topics for a subject"""
    from app.models.subject import Topic
    topics = Topic.query.filter_by(
        subject_id=subject_id,
        is_active=True
    ).order_by(Topic.order_index).all()

    return jsonify([{
        'id': t.id,
        'name': t.name_sk,
        'slug': t.slug,
        'difficulty': t.difficulty
    } for t in topics])
