import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    mariadb_pass = os.environ.get("MYSQL_ROOT_PASSWORD")
    mariadb_host = os.environ.get("MYSQL_HOST")

    app.config["SECRET_KEY"] = os.urandom(24).hex()
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "mysql+pymysql://root:" + mariadb_pass + "@" + mariadb_host + "/footdraw"
    )

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    from .models import User

    with app.app_context():

        # Create tables
        db.create_all()

        # add admin user to the database
        user = User.query.filter_by(id="admin").first()
        if not user:
            new_user = User(
                id="admin",
                name="Administrator",
                groupid=0,
                password=generate_password_hash("F00tDr4w", method="pbkdf2:sha256"),
                admin="X",
                email=" ",
            )
            db.session.add(new_user)
            db.session.commit()

    @login_manager.user_loader
    def load_user(userid):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(userid)

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint

    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint

    app.register_blueprint(main_blueprint)
    
    return app
