from app import create_app

app = create_app()
# Remove or ignore app.run() in production
# Render will use gunicorn to start the app
