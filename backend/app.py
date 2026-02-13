from flask import Flask
from flask_cors import CORS

from routes.procedure_routes import procedure_bp
from routes.sqltest_routes import sqltest_bp


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)
    app.register_blueprint(procedure_bp)
    app.register_blueprint(sqltest_bp)

    @app.get('/health')
    def health_check():
        return {"status": "ok"}, 200

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
