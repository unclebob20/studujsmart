from datetime import datetime
from flask_login import UserMixin
from app import db
import bcrypt


class User(UserMixin, db.Model):
    """User model"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    username = db.Column(db.String(100))
    password_hash = db.Column(db.String(255))

    # OAuth fields
    oauth_provider = db.Column(db.String(50))  # 'google', 'facebook', 'tiktok'
    oauth_id = db.Column(db.String(255))

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

    # Onboarding data
    full_name = db.Column(db.String(255))
    grade = db.Column(db.Integer)  # 1-4 for high school
    birth_year = db.Column(db.Integer)
    goal = db.Column(db.String(50))  # 'matura', 'kontrola', 'learning'
    onboarding_completed = db.Column(db.Boolean, default=False)

    # Gamification
    xp = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    streak_days = db.Column(db.Integer, default=0)
    last_activity_date = db.Column(db.Date)

    # Relationships
    subscription = db.relationship('Subscription', backref='user', uselist=False,
                                   cascade='all, delete-orphan')
    test_sessions = db.relationship('TestSession', backref='user',
                                    cascade='all, delete-orphan')
    user_subjects = db.relationship('UserSubject', backref='user',
                                    cascade='all, delete-orphan')
    badges = db.relationship('UserBadge', backref='user',
                             cascade='all, delete-orphan')

    __table_args__ = (
        db.UniqueConstraint('oauth_provider', 'oauth_id',
                            name='uix_oauth_provider_id'),
    )

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

    def check_password(self, password):
        """Verify password"""
        if not self.password_hash:
            return False
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )

    def add_xp(self, amount):
        """Add XP and check for level up"""
        self.xp += amount
        new_level = self.calculate_level()
        if new_level > self.level:
            self.level = new_level
            return True  # Leveled up!
        return False

    def calculate_level(self):
        """Calculate level based on XP"""
        # Level thresholds: 1=0, 2=100, 3=250, 4=500, 5=1000, etc.
        thresholds = [0, 100, 250, 500, 1000, 2000, 4000, 7000, 11000, 16000]
        for i, threshold in enumerate(thresholds):
            if self.xp < threshold:  # ✅ Use self.xp, not User.xp
                return i
        return len(thresholds)

    def update_streak(self):
        """Update daily streak"""
        from datetime import date, timedelta

        today = date.today()

        if not self.last_activity_date:
            # First activity ever
            self.streak_days = 1
            self.last_activity_date = today
        elif self.last_activity_date == today:
            # Already active today
            pass
        elif self.last_activity_date == today - timedelta(days=1):
            # Active yesterday, continue streak
            self.streak_days += 1
            self.last_activity_date = today
        else:
            # Streak broken
            self.streak_days = 1
            self.last_activity_date = today

    def __repr__(self):
        return f'<User {self.email}>'


class UserSubject(db.Model):
    """User's selected subjects"""
    __tablename__ = 'user_subjects'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete='CASCADE'))
    is_active = db.Column(db.Boolean, default=True)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'subject_id', name='uix_user_subject'),
    )
