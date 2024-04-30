from flask import Flask
from settings import API_KEY,LOGGING_LEVEL
from routes import bp as routes_bp
from models import db
import coloredlogs
# import logging

coloredlogs.install(level=LOGGING_LEVEL.upper(), fmt='%(asctime)s [%(levelname)s] [%(funcName)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S', colors={'DEBUG': 'green', 'INFO': 'blue', 'WARNING': 'yellow', 'ERROR': 'red', 'CRITICAL': 'bold_red'})


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