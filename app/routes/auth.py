from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, current_user
from authlib.integrations.flask_client import OAuth
from datetime import datetime
from app import db
from app.models.user import User, UserSubject
from app.models.subscription import Subscription

auth_bp = Blueprint('auth', __name__)

# Initialize OAuth
oauth = OAuth()


def init_oauth(app):
    """Initialize OAuth with app"""
    oauth.init_app(app)

    # Google OAuth
    oauth.register(
        name='google',
        client_id=app.config.get('GOOGLE_CLIENT_ID'),
        client_secret=app.config.get('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )

    # Facebook OAuth
    oauth.register(
        name='facebook',
        client_id=app.config.get('FACEBOOK_CLIENT_ID'),
        client_secret=app.config.get('FACEBOOK_CLIENT_SECRET'),
        access_token_url='https://graph.facebook.com/oauth/access_token',
        authorize_url='https://www.facebook.com/dialog/oauth',
        api_base_url='https://graph.facebook.com/',
        client_kwargs={'scope': 'email public_profile'},
    )


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Validate
        if not email or not password:
            flash('Email a heslo sú povinné', 'error')
            return render_template('auth/register.html')

        if password != confirm_password:
            flash('Heslá sa nezhodujú', 'error')
            return render_template('auth/register.html')

        if len(password) < 6:
            flash('Heslo musí mať aspoň 6 znakov', 'error')
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
        flash('Registrácia úspešná! 🎉', 'success')

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
        remember = request.form.get('remember') == 'on'

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash('Nesprávny email alebo heslo', 'error')
            return render_template('auth/login.html')

        login_user(user, remember=remember)
        user.last_login = datetime.utcnow()
        db.session.commit()

        flash('Vitaj späť! 👋', 'success')

        # Redirect to onboarding if not completed
        if not user.onboarding_completed:
            return redirect(url_for('auth.onboarding'))

        return redirect(url_for('dashboard.index'))

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    """User logout"""
    logout_user()
    flash('Bol si odhlásený', 'info')
    return redirect(url_for('auth.login'))


# =============================================================================
# Google OAuth Routes
# =============================================================================
@auth_bp.route('/login/google')
def google_login():
    """Initiate Google OAuth login"""
    redirect_uri = url_for('auth.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@auth_bp.route('/login/google/callback')
def google_callback():
    """Google OAuth callback"""
    try:
        token = oauth.google.authorize_access_token()
        user_info = token.get('userinfo')

        if not user_info:
            flash('Nepodarilo sa získať informácie z Google', 'error')
            return redirect(url_for('auth.login'))

        email = user_info.get('email')
        google_id = user_info.get('sub')
        name = user_info.get('name')

        # Check if user exists
        user = User.query.filter_by(email=email).first()

        if not user:
            # Create new user
            user = User(
                email=email,
                oauth_provider='google',
                oauth_id=google_id,
                full_name=name
            )
            db.session.add(user)

            # Create free subscription
            subscription = Subscription(user=user, plan='free', status='active')
            db.session.add(subscription)

            db.session.commit()

            login_user(user)
            flash('Účet vytvorený! 🎉', 'success')
            return redirect(url_for('auth.onboarding'))
        else:
            # Update OAuth info if not set
            if not user.oauth_provider:
                user.oauth_provider = 'google'
                user.oauth_id = google_id

            user.last_login = datetime.utcnow()
            db.session.commit()

            login_user(user)
            flash('Vitaj späť! 👋', 'success')

            if not user.onboarding_completed:
                return redirect(url_for('auth.onboarding'))

            return redirect(url_for('dashboard.index'))

    except Exception as e:
        flash('Chyba pri prihlásení cez Google', 'error')
        print(f"Google OAuth error: {e}")
        return redirect(url_for('auth.login'))


# =============================================================================
# Facebook OAuth Routes
# =============================================================================
@auth_bp.route('/login/facebook')
def facebook_login():
    """Initiate Facebook OAuth login"""
    redirect_uri = url_for('auth.facebook_callback', _external=True)
    return oauth.facebook.authorize_redirect(redirect_uri)


@auth_bp.route('/login/facebook/callback')
def facebook_callback():
    """Facebook OAuth callback"""
    try:
        token = oauth.facebook.authorize_access_token()

        # Get user info from Facebook
        resp = oauth.facebook.get('me?fields=id,name,email')
        user_info = resp.json()

        email = user_info.get('email')
        if not email:
            flash('Nepodarilo sa získať email z Facebook', 'error')
            return redirect(url_for('auth.login'))

        facebook_id = user_info.get('id')
        name = user_info.get('name')

        # Check if user exists
        user = User.query.filter_by(email=email).first()

        if not user:
            # Create new user
            user = User(
                email=email,
                oauth_provider='facebook',
                oauth_id=facebook_id,
                full_name=name
            )
            db.session.add(user)

            # Create free subscription
            subscription = Subscription(user=user, plan='free', status='active')
            db.session.add(subscription)

            db.session.commit()

            login_user(user)
            flash('Účet vytvorený! 🎉', 'success')
            return redirect(url_for('auth.onboarding'))
        else:
            # Update OAuth info if not set
            if not user.oauth_provider:
                user.oauth_provider = 'facebook'
                user.oauth_id = facebook_id

            user.last_login = datetime.utcnow()
            db.session.commit()

            login_user(user)
            flash('Vitaj späť! 👋', 'success')

            if not user.onboarding_completed:
                return redirect(url_for('auth.onboarding'))

            return redirect(url_for('dashboard.index'))

    except Exception as e:
        flash('Chyba pri prihlásení cez Facebook', 'error')
        print(f"Facebook OAuth error: {e}")
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

        if not subject_ids:
            flash('Prosím, vyber aspoň jeden predmet', 'error')
            from app.models.subject import Subject
            subjects = Subject.query.filter_by(is_active=True).order_by(Subject.order_index).all()
            return render_template('auth/onboarding.html', subjects=subjects)

        for subject_id in subject_ids:
            user_subject = UserSubject(
                user_id=current_user.id,
                subject_id=int(subject_id)
            )
            db.session.add(user_subject)

        db.session.commit()
        flash(f'Vitaj v ŠtúdujSmart, {current_user.full_name}! 🎓', 'success')

        return redirect(url_for('dashboard.index'))

    # Get available subjects
    from app.models.subject import Subject
    subjects = Subject.query.filter_by(is_active=True).order_by(Subject.order_index).all()

    return render_template('auth/onboarding.html', subjects=subjects)
