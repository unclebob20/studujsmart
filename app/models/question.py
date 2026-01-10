from datetime import datetime
from app import db


class QuestionTemplate(db.Model):
    """Pre-generated question templates"""
    __tablename__ = 'question_templates'

    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id', ondelete='CASCADE'))

    question_type = db.Column(db.String(50), nullable=False)  # 'single_choice', 'numeric', 'fill_blank'
    difficulty = db.Column(db.String(20), nullable=False)

    # Template with placeholders: "Solve: {a}x² + {b}x + {c} = 0"
    question_template = db.Column(db.Text, nullable=False)

    # JSON: {"a": {"min": 1, "max": 10}, "b": {...}}
    variables = db.Column(db.JSON)

    # Correct answer formula/template
    correct_answer_template = db.Column(db.Text)

    # For multiple choice - array of choice templates
    choices_template = db.Column(db.JSON)

    # Explanation template
    explanation_template = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    times_used = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<QuestionTemplate {self.id} type={self.question_type}>'


class Question(db.Model):
    """Generated questions (cache + history)"""
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('question_templates.id'))
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'))

    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)

    correct_answer = db.Column(db.Text, nullable=False)
    choices = db.Column(db.JSON)  # For multiple choice: ["A) x=2", "B) x=3", ...]
    explanation = db.Column(db.Text)

    # Variables used for this variation
    variables_used = db.Column(db.JSON)  # {"a": 5, "b": 3, "c": -2}

    # Caching & stats
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    times_used = db.Column(db.Integer, default=0)
    avg_correct_rate = db.Column(db.Numeric(5, 2))

    def __repr__(self):
        return f'<Question {self.id} type={self.question_type}>'