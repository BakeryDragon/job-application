from flask import Flask

from app.database import init_db
from app.routes import routes

app = Flask(__name__)
app.register_blueprint(routes)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
