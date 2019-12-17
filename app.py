#!/usr/bin/env python3

from App.flask import app, sql
from App.config import FLASK_HOST, FLASK_PORT

if __name__ == "__main__":
    sql.create_all()
    app.run(FLASK_HOST, FLASK_PORT)
