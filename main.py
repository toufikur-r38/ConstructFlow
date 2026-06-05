import os
from dotenv import load_dotenv

if os.environ.get("FLASK_ENV") != "production":
    load_dotenv()

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=app.config["IS_DEVELOPMENT"])
