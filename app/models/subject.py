from datetime import datetime
from app import db


class Subject(db.Model):
    """Subject model (Math, Slovak, English, etc.)"""
    __tablename__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True)
    name_sk = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100))
    slug = db.Column(db.String(50), unique=True, nullable=False)

    icon = db.Column(db.String(50))  # emoji or icon class
    color = db.Column(db.String(7))  # hex color

    is_active = db.Column(db.Boolean, default=True)
    order_index = db.Column(db.Integer, default=0)

    # Relationships
    topics = db.relationship('Topic', backref='subject', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Subject {self.name_sk}>'


class Topic(db.Model):
    """Topic within a subject"""
    __tablename__ = 'topics'

    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete='CASCADE'))
    parent_topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'))

    name_sk = db.Column(db.String(200), nullable=False)
    name_en = db.Column(db.String(200))
    slug = db.Column(db.String(100), nullable=False)

    description = db.Column(db.Text)
    difficulty = db.Column(db.String(20))  # 'easy', 'medium', 'hard'

    is_active = db.Column(db.Boolean, default=True)
    order_index = db.Column(db.Integer, default=0)

    # Relationships
    subtopics = db.relationship('Topic', backref=db.backref('parent', remote_side=[id]))
    questions = db.relationship('Question', backref='topic', cascade='all, delete-orphan')

    __table_args__ = (
        db.UniqueConstraint('subject_id', 'slug', name='uix_subject_slug'),
    )

    def __repr__(self):
        return f'<Topic {self.name_sk}>'


class UserTopicProgress(db.Model):
    """User's progress per topic"""
    __tablename__ = 'user_topic_progress'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id', ondelete='CASCADE'))

    total_questions = db.Column(db.Integer, default=0)
    correct_answers = db.Column(db.Integer, default=0)
    accuracy_rate = db.Column(db.Numeric(5, 2), default=0)

    last_practiced_at = db.Column(db.DateTime)
    mastery_level = db.Column(db.String(20), default='beginner')  # 'beginner', 'intermediate', 'advanced', 'master'

    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'topic_id', name='uix_user_topic'),
    )

    def update_progress(self, is_correct):
        """Update progress after answering a question"""
        if self.total_questions is None:
            self.total_questions = 0
        if self.correct_answers is None:
            self.correct_answers = 0

        self.total_questions += 1
        if is_correct:
            self.correct_answers += 1

        self.accuracy_rate = (self.correct_answers / self.total_questions) * 100
        self.mastery_level = self._calculate_mastery()
        self.last_practiced_at = datetime.utcnow()

    def _calculate_mastery(self):
        """Calculate mastery level based on accuracy"""
        if self.accuracy_rate >= 90:
            return 'master'
        elif self.accuracy_rate >= 75:
            return 'advanced'
        elif self.accuracy_rate >= 60:
            return 'intermediate'
        else:
            return 'beginner'
