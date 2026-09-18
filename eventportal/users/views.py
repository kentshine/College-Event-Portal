from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from eventportal import db
from eventportal.users.forms import LoginForm, RegistrationForm
from eventportal.models import User, Ticket

users = Blueprint('users', __name__)


@users.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        username = form.username.data
        department = form.department.data
        semester = form.semester.data
        
        user = User(email=email, password=password,username=username,department=department,semester=semester)
        db.session.add(user)
        db.session.commit()
        flash("Thanks for registering! Now you can login!")
        print(user)
        return redirect(url_for('users.login'))
    elif request.method == "POST":
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text if hasattr(getattr(form, field), 'label') else field}: {error}")
        print("Register form validation failed:", form.errors)

    return render_template('register.html', form=form)


@users.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()

        if user is None or not user.check_password(password):
            flash("Email or password is incorrect")
            return render_template('login.html', form=form)

        login_user(user)
        next_page = request.args.get('next')

        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('core.index')

        flash("Logged in Successfully")
        print("Logged in as ", user)
        return redirect(next_page)
    elif request.method == "POST":
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text if hasattr(getattr(form, field), 'label') else field}: {error}")
        print("Login form validation failed:", form.errors)

    return render_template('login.html', form=form)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('core.index'))

@users.route("/my-tickets")
@login_required
def my_tickets():
    tickets = Ticket.query.filter_by(user_id=current_user.id).order_by(Ticket.booking_date.desc()).all()
    return render_template('tickets.html', tickets=tickets)
