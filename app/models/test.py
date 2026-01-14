from datetime import datetime
from app import db


class TestSession(db.Model):
    """Test session"""
    __tablename__ = 'test_sessions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))

    test_type = db.Column(db.String(50), nullable=False)  # 'quick', 'custom'

    # Test settings
    total_questions = db.Column(db.Integer, nullable=False)
    difficulty = db.Column(db.String(20))
    topic_ids = db.Column(db.ARRAY(db.Integer))  # For custom tests

    # Status
    status = db.Column(db.String(20), nullable=False, default='in_progress')  # 'in_progress', 'completed', 'abandoned'

    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    # Results
    score = db.Column(db.Integer)
    percentage = db.Column(db.Numeric(5, 2))
    time_spent_seconds = db.Column(db.Integer)

    # Relationships
    answers = db.relationship('UserAnswer', backref='session', cascade='all, delete-orphan')
    subject = db.relationship('Subject')

    def calculate_results(self):
        """Calculate and store test results"""
        # FIX: Convert relationship to list using .all()
        answers = self.answers.all() if hasattr(self.answers, 'all') else list(self.answers)

        correct = sum(1 for a in answers if a.is_correct)
        self.score = correct
        self.percentage = (correct / self.total_questions) * 100 if self.total_questions > 0 else 0

        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            self.time_spent_seconds = int(delta.total_seconds())

    def __repr__(self):
        return f'<TestSession {self.id} user={self.user_id}>'

class UserAnswer(db.Model):
    """User's answer to a question"""
    __tablename__ = 'user_answers'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('test_sessions.id', ondelete='CASCADE'))
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    user_answer = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)

    # Explanation tracking
    explanation_viewed = db.Column(db.Boolean, default=False)
    explanation_viewed_at = db.Column(db.DateTime)
    ai_explanation = db.Column(db.Text)  # ADD THIS LINE

    time_spent_seconds = db.Column(db.Integer)
    answered_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    question = db.relationship('Question')
    def __repr__(self):
        return f'<UserAnswer session={self.session_id} question={self.question_id}>'



