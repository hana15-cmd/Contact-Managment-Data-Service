from app import create_app
from app.views import init_db_scheme


app = create_app()

if __name__ == '__main__':
    init_db_scheme()
    app.run(debug=True)