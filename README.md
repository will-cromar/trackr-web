# trackr-web
Web component of project for COP 4331.

To use, make an executable run.py file with:

`from app import app`

`app.run(debug=True)`

You'll need to install the requirements in requirements with pip in a *Python 3* environment. A virtual environment is recommended. (Google "python venv" if you don't know what that is.)

To create the necessary database tables for your app, visit the `/init` endpoint while the server is running.

The application will create a SQLite database by default. To use a different database, simply set the `DATABASE_URL` environment variable to the URI for the database you want to connect to. (For example, `postgres:///trackr`.)
