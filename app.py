from flask import Flask
from settings import API_KEY
from routes import bp as routes_bp
from models import db


# create the app
app = Flask(__name__)
# cors = CORS(app)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{app.root_path}/Reddit.db"
app.config['API_KEY'] = API_KEY

# # initialize the app with the extension
db.init_app(app)


app.register_blueprint(routes_bp)

if __name__ == "__main__":
    app.run(debug=True)