from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app import db
from app.models.user import User
from app.models.subscription import Subscription

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Validate
        if not email or not password:
            flash('Email a heslo sú povinné', 'error')
            return render_template('auth/register.html')

        # Check if user exists
        if User.query.filter_by(email=email).first():
            flash('Email je už registrovaný', 'error')
            return render_template('auth/register.html')

        # Create user
        user = User(email=email)
        user.set_password(password)
        db.session.add(user)

        # Create free subscription
        subscription = Subscription(user=user, plan='free', status='active')
        db.session.add(subscription)

        db.session.commit()

        # Auto-login
        login_user(user)
        flash('Registrácia úspešná!', 'success')

        return redirect(url_for('auth.onboarding'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash('Nesprávny email alebo heslo', 'error')
            return render_template('auth/login.html')

        login_user(user, remember=True)
        user.last_login = datetime.utcnow()
        db.session.commit()

        # Redirect to onboarding if not completed
        if not user.onboarding_completed:
            return redirect(url_for('auth.onboarding'))

        return redirect(url_for('dashboard.index'))

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    """User logout"""
    logout_user()
    flash('Boli ste odhlásený', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/onboarding', methods=['GET', 'POST'])
def onboarding():
    """Onboarding flow for new users"""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    if current_user.onboarding_completed:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        current_user.full_name = request.form.get('full_name')
        current_user.grade = int(request.form.get('grade', 0))
        current_user.birth_year = int(request.form.get('birth_year', 0))
        current_user.goal = request.form.get('goal')
        current_user.onboarding_completed = True

        # Add selected subjects
        subject_ids = request.form.getlist('subjects')
        from app.models.user import UserSubject

        for subject_id in subject_ids:
            user_subject = UserSubject(
                user_id=current_user.id,
                subject_id=int(subject_id)
            )
            db.session.add(user_subject)

        db.session.commit()
        flash('Vitaj v ŠtúdujSmart! 🎓', 'success')

        return redirect(url_for('dashboard.index'))

    # Get available subjects
    from app.models.subject import Subject
    subjects = Subject.query.filter_by(is_active=True).order_by(Subject.order_index).all()

    return render_template('auth/onboarding.html', subjects=subjects)
