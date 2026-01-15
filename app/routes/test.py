from flask import Blueprint, render_template, redirect, url_for, request, jsonify, abort, flash
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models.subject import Subject
from app.models.test import TestSession, UserAnswer
from app.models.question import Question

test_bp = Blueprint('test', __name__)


# Lazy load services to avoid import errors
def get_test_service():
    from app.services.test_service import TestService
    return TestService()


def get_ai_service():
    from app.services.ai_service import AIService
    return AIService()


@test_bp.route('/quick/<int:subject_id>')
@login_required
def quick_test(subject_id):
    """Quick test start page"""
    subject = Subject.query.get_or_404(subject_id)
    return render_template('test/quick.html', subject=subject)


@test_bp.route('/quick/<int:subject_id>/start', methods=['POST'])
@login_required
def start_quick_test(subject_id):
    """Start a new quick test"""
    try:
        print(f"Step 1: Starting test for subject {subject_id}")

        # Create test session
        test_service = get_test_service()
        print(f"Step 2: Got test service: {test_service}")

        test_session = test_service.create_quick_test(
            user_id=current_user.id,
            subject_id=subject_id,
            num_questions=10
        )
        print(f"Step 3: Created test session: {test_session.id}")

        # Update user streak
        current_user.update_streak()
        db.session.commit()

        return redirect(url_for('test.take_test', session_id=test_session.id))

    except Exception as e:
        import traceback
        print(f"ERROR: {e}")
        traceback.print_exc()
        flash('Chyba pri vytváraní testu', 'error')
        return redirect(url_for('dashboard.index'))



@test_bp.route('/<int:session_id>')
@login_required
def take_test(session_id):
    """Test-taking interface"""
    test_session = TestSession.query.get_or_404(session_id)

    # Verify it's user's test
    if test_session.user_id != current_user.id:
        abort(403)

    # If already completed, redirect to results
    if test_session.status == 'completed':
        return redirect(url_for('test.results', session_id=session_id))

    return render_template('test/take.html', test_session=test_session)


@test_bp.route('/<int:session_id>/results')
@login_required
def results(session_id):
    """View test results"""
    test_session = TestSession.query.get_or_404(session_id)

    # Verify it's user's test
    if test_session.user_id != current_user.id:
        abort(403)

    # Get all answers
    answers = UserAnswer.query.filter_by(
        session_id=session_id
    ).order_by(UserAnswer.id).all()

    # Calculate XP earned
    xp_earned = test_session.score * 10  # 10 XP per correct answer
    if test_session.percentage == 100:
        xp_earned += 50  # Bonus for perfect score

    return render_template(
        'test/results.html',
        test_session=test_session,
        answers=answers,
        xp_earned=xp_earned
    )


# =============================================================================
# API ENDPOINTS
# =============================================================================

@test_bp.route('/test-route')
def test_route():
    return "Test route works!"

@test_bp.route('/tests/<int:session_id>/questions', methods=['GET'])
@login_required
def api_get_questions(session_id):
    """Get all questions for a test session"""
    test_session = TestSession.query.get_or_404(session_id)

    # Verify ownership
    if test_session.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    # Get questions for this test
    # For now, we'll query questions created for this topic
    # In production, you'd have a proper many-to-many relationship
    questions = Question.query.filter(
        Question.topic_id.in_(test_session.topic_ids)
    ).limit(test_session.total_questions).all()

    test_service = get_test_service()

    # If no questions exist, generate them now
    if not questions or len(questions) < test_session.total_questions:
        questions = test_service._generate_questions_for_test(
            test_session,
            test_session.topic_ids,
            test_session.total_questions
        )

    return jsonify({
        'questions': [{
            'id': q.id,
            'question_text': q.question_text,
            'question_type': q.question_type,
            'difficulty': q.difficulty,
            'choices': q.choices
        } for q in questions]
    })


@test_bp.route('/tests/<int:session_id>/answer', methods=['POST'])
@login_required
def api_submit_answer(session_id):
    """Submit an answer"""
    test_session = TestSession.query.get_or_404(session_id)

    # Verify ownership
    if test_session.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    test_service = get_test_service()

    data = request.get_json()
    question_id = data.get('question_id')
    answer = data.get('answer')
    time_spent = data.get('time_spent', 0)

    # Check if already answered
    existing = UserAnswer.query.filter_by(
        session_id=session_id,
        question_id=question_id
    ).first()

    if existing:
        # Update existing answer
        existing.user_answer = answer
        existing.is_correct = test_service._check_answer(
            Question.query.get(question_id),
            answer
        )
        db.session.commit()
        return jsonify({'success': True, 'updated': True})

    # Create new answer
    try:
        user_answer = test_service.submit_answer(
            session_id=session_id,
            question_id=question_id,
            user_id=current_user.id,
            user_answer=answer,
            time_spent=time_spent
        )

        return jsonify({
            'success': True,
            'is_correct': user_answer.is_correct
        })

    except Exception as e:
        print(f"Error submitting answer: {e}")
        return jsonify({'error': str(e)}), 500


@test_bp.route('/tests/<int:session_id>/complete', methods=['POST'])
@login_required
def api_complete_test(session_id):
    """Mark test as complete"""
    test_session = TestSession.query.get_or_404(session_id)

    # Verify ownership
    if test_session.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    test_service = get_test_service()

    try:
        # Complete test
        test_service.complete_test(session_id)

        # Refresh test_session from database to get updated values
        db.session.refresh(test_session)

        # Safety check - if score is still None, set to 0
        if test_session.score is None:
            test_session.score = 0
            test_session.percentage = 0
            db.session.commit()

        # Award XP
        xp_earned = test_session.score * 10
        percentage = float(test_session.percentage) if test_session.percentage else 0
        if percentage == 100:
            xp_earned += 50  # Perfect score bonus

        leveled_up = current_user.add_xp(xp_earned)
        db.session.commit()

        return jsonify({
            'success': True,
            'xp_earned': xp_earned,
            'leveled_up': leveled_up,
            'new_level': current_user.level
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@test_bp.route('/answers/<int:answer_id>/explanation', methods=['GET'])
@login_required
def api_get_explanation(answer_id):
    """Get AI explanation for an answer"""
    answer = UserAnswer.query.get_or_404(answer_id)

    # Verify ownership
    if answer.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    # If already generated, return it
    if answer.ai_explanation:
        return jsonify({
            'explanation': answer.ai_explanation
        })

    # Generate new explanation
    ai_service = get_ai_service()

    try:
        explanation = ai_service.generate_explanation(
            question_text=answer.question.question_text,
            correct_answer=answer.question.correct_answer,
            user_answer=answer.user_answer,
            subject=answer.session.subject.name_sk
        )

        # Store explanation
        answer.ai_explanation = explanation
        answer.explanation_viewed = True
        answer.explanation_viewed_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'explanation': explanation
        })

    except Exception as e:
        print(f"Error generating explanation: {e}")
        # Fallback to template explanation if available
        fallback = answer.question.explanation or 'Vysvetlenie nedostupné'
        return jsonify({
            'explanation': fallback
        })

@test_bp.route('/create', methods=['POST'])
@login_required
def create_test():
    """Create a new test session (used by dashboard)"""
    try:
        # Get parameters from form or JSON
        subject_id = request.form.get('subject_id') or request.get_json().get('subject_id')
        topic_id = request.form.get('topic_id') or request.get_json().get('topic_id')
        num_questions = int(request.form.get('num_questions', 10) or request.get_json().get('num_questions', 10))

        test_service = get_test_service()

        # Create test session
        if topic_id:
            # Test for specific topic
            test_session = test_service.create_topic_test(
                user_id=current_user.id,
                topic_id=int(topic_id),
                num_questions=num_questions
            )
        else:
            # Quick test for subject
            test_session = test_service.create_quick_test(
                user_id=current_user.id,
                subject_id=int(subject_id),
                num_questions=num_questions
            )

        # Update user streak
        current_user.update_streak()
        db.session.commit()

        # Redirect to take test
        return redirect(url_for('test.take_test', session_id=test_session.id))

    except Exception as e:
        import traceback
        print(f"ERROR: {e}")
        traceback.print_exc()
        flash('Chyba pri vytváraní testu', 'error')
        return redirect(url_for('dashboard.index'))