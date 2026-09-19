import os
from flask import Flask
from flask_migrate import Migrate
from flask_admin import Admin
from flask_admin.menu import MenuLink
from flask_mail import Mail,Message
from eventportal.models import User,Event
from eventportal.models import login_manager,db
from eventportal.models import EventView,UserView,MyAdminIndexView

app = Flask(__name__)

########## APP CONFIG #############
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', '1234')
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'jyothieventportal@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'wquiwxnpegezlhjb')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
## mail ###
mail = Mail(app)

######### DATABASE CONFIG ##############
basedir = os.path.abspath(os.path.dirname(__file__))

# Fetch database URL from environment, or use SQLite locally
db_url = os.environ.get('DATABASE_URL', 'sqlite:///' + os.path.join(basedir, 'data.sqlite'))
# Render's PostgreSQL URL starts with 'postgres://', but SQLAlchemy requires 'postgresql://'
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)
    
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app,db)



## admin ##
admin_id = 999
admin = Admin(app, name='AdminDesk', template_mode='bootstrap4', base_template='admin/master.html', index_view=MyAdminIndexView())
admin.add_view(EventView(Event,db.session))
admin.add_view(UserView(User,db.session))
admin.add_link(MenuLink(name='Events', url='/download', category='Download'))
admin.add_link(MenuLink(name='← Back to Site', url='/'))




###################################
######### LOGIN CONFIG ############
###################################
login_manager.init_app(app)
login_manager.login_view = 'users.login'

###############################
###### BLUEPRINT CONFIGS ######
###############################

from eventportal.core.views import core
from eventportal.users.views import users
from eventportal.events.views import events
from eventportal.error_pages.handler import error_pages


# Register the app
app.register_blueprint(users)
app.register_blueprint(events)
app.register_blueprint(core)
app.register_blueprint(error_pages)
