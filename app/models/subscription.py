from datetime import datetime
from app import db


class Subscription(db.Model):
    """Subscription model"""
    __tablename__ = 'subscriptions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'),
                        unique=True)

    plan = db.Column(db.String(20), nullable=False, default='free')  # 'free', 'basic', 'premium'
    status = db.Column(db.String(20), nullable=False, default='active')  # 'active', 'cancelled', 'expired', 'trial'

    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    cancelled_at = db.Column(db.DateTime)

    # Payment info
    payment_provider = db.Column(db.String(50))  # 'stripe', 'comgate', 'bank_transfer'
    payment_id = db.Column(db.String(255))

    # Trial
    is_trial = db.Column(db.Boolean, default=False)
    trial_ends_at = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def is_active_subscription(self):
        """Check if subscription is currently active"""
        if self.status == 'expired' or self.status == 'cancelled':
            return False

        if self.expires_at and self.expires_at < datetime.utcnow():
            return False

        return True

    def get_plan_limits(self):
        """Get limits for current plan"""
        limits = {
            'free': {
                'tests_per_day': 5,
                'explanations': False,
                'custom_tests': False,
                'ai_chat': False,
                'max_stats_days': 7
            },
            'basic': {
                'tests_per_day': 30,
                'explanations': True,
                'custom_tests': True,
                'ai_chat': False,
                'max_stats_days': 365
            },
            'premium': {
                'tests_per_day': 999,
                'explanations': True,
                'custom_tests': True,
                'ai_chat': True,
                'max_stats_days': 365
            }
        }

        return limits.get(self.plan, limits['free'])

    def __repr__(self):
        return f'<Subscription user={self.user_id} plan={self.plan}>'


class UsageLimit(db.Model):
    """Daily usage tracking"""
    __tablename__ = 'usage_limits'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))

    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    tests_taken = db.Column(db.Integer, default=0)
    ai_explanations_viewed = db.Column(db.Integer, default=0)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'date', name='uix_user_date'),
    )

    @staticmethod
    def get_today_usage(user_id):
        """Get or create today's usage record"""
        from datetime import date

        today = date.today()
        usage = UsageLimit.query.filter_by(
            user_id=user_id,
            date=today
        ).first()

        if not usage:
            usage = UsageLimit(user_id=user_id, date=today)
            db.session.add(usage)
            db.session.commit()

        return usage
