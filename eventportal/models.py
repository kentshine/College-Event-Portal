import threading
import uuid
from datetime import datetime
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose, AdminIndexView
from flask import redirect,render_template,url_for,Response,request
from werkzeug.exceptions import HTTPException

db = SQLAlchemy()
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


registered = db.Table('registered',
                      db.Column('user_id',db.Integer,db.ForeignKey('users.id'),primary_key=True),
                      db.Column('event_id',db.Integer,db.ForeignKey('event.id'),primary_key=True)
                      )

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and getattr(current_user, 'is_admin', False)

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('users.login', next=request.url))

    @expose('/')
    def index(self):
        from eventportal.models import Ticket
        events = Event.query.order_by(Event.event_date.asc()).all()
        # Build a dict of event_id -> list of users for template use
        event_attendees = {}
        for event in events:
            tickets = Ticket.query.filter_by(event_id=event.id).all()
            event_attendees[event.id] = [t.user for t in tickets]
        return self.render('admin/index.html', events=events, event_attendees=event_attendees)

class EventView(ModelView):
    # Only include literal columns, completely exclude all relationships to prevent NotNull violations
    form_columns = ['title', 'event_date', 'event_time', 'location', 'description', 'calendar_id', 'wallpaper']

    def is_accessible(self):
        return current_user.is_authenticated and getattr(current_user, 'is_admin', False)

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('users.login', next=request.url))

    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        return redirect(url_for('events.create'))

class UserView(ModelView):
    # Only include literal columns, completely exclude all relationships to prevent NotNull violations
    form_columns = ['username', 'email', 'department', 'semester', 'is_admin']

    def is_accessible(self):
        return current_user.is_authenticated and getattr(current_user, 'is_admin', False)

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('users.login', next=request.url))

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64))
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    event = db.relationship('Event', backref='creator', lazy=True)
    department = db.Column(db.String(64))
    semester = db.Column(db.String(64))
    registered_events = db.relationship('Event',secondary=registered,backref=db.backref('coming',lazy='dynamic'))


    def __init__(self, email, password,username,semester,department):
        self.username = username
        self.semester = semester
        self.department = department
        self.email = email
        self.password_hash = generate_password_hash(password)



    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"Email: {self.email}"


class Event(db.Model):
    users = db.relationship(User)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(140), nullable=False)
    event_date = db.Column(db.String,nullable=False)
    event_time = db.Column(db.String,nullable=False)
    location = db.Column(db.String,nullable=False)
    description = db.Column(db.Text, nullable=False)
    calendar_id = db.Column(db.String,nullable=False)
    wallpaper = db.Column(db.String,nullable=False,default="nothing.jpg")

    def __init__(self,user_id,title,event_date,event_time,location,description,calendar_id):
        self.user_id = user_id
        self.title = title
        self.event_date = event_date
        self.event_time = event_time
        self.location = location
        self.description = description
        self.calendar_id = calendar_id

    def __repr__(self):
        return f"Event Id: {self.id} --- Date: {self.event_date} --- Title: {self.title} --- Created By:{self.user_id}"

class Ticket(db.Model):
    __tablename__ = 'tickets'
    id = db.Column(db.Integer, primary_key=True)
    ticket_number = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('my_tickets', lazy=True, viewonly=True, overlaps="coming,registered_events"))
    event = db.relationship('Event', backref=db.backref('event_tickets', lazy=True, viewonly=True))



class NewThreadedTask(threading.Thread):
    def __init__(self):
        super(NewThreadedTask,self).__init__()

    def run(self):
        try:
            print("threaded task has been completed")
        except Exception:
            print("Error Occured !!")
