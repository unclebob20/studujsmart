from datetime import datetime
from app import db


class Badge(db.Model):
    """Badge definitions"""
    __tablename__ = 'badges'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    name_sk = db.Column(db.String(100), nullable=False)
    description_sk = db.Column(db.Text)
    icon = db.Column(db.String(50))  # emoji or icon class

    # Condition for earning
    condition_type = db.Column(db.String(50))  # 'tests_completed', 'streak_days', 'accuracy_rate'
    condition_value = db.Column(db.Integer)

    xp_reward = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Badge {self.slug}>'


class UserBadge(db.Model):
    """Badges earned by users"""
    __tablename__ = 'user_badges'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    badge_id = db.Column(db.Integer, db.ForeignKey('badges.id', ondelete='CASCADE'))

    earned_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    badge = db.relationship('Badge')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'badge_id', name='uix_user_badge'),
    )

    def __repr__(self):
        return f'<UserBadge user={self.user_id} badge={self.badge_id}>'