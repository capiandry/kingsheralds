# kingsheralds

Simple instructions to deploy this Django project to Render.

Prerequisites
- A GitHub repository connected to Render.
- A Render account with a Python Web Service.

Deploy steps
1. Push branch `render-deploy` to GitHub (or `main` if you prefer).
2. On Render, create a new Web Service and connect the repository.
3. Set environment variables on Render:
   - `DJANGO_SECRET_KEY` — a secure random string
   - `DJANGO_DEBUG` — `False` for production
   - `DJANGO_ALLOWED_HOSTS` — comma-separated hostnames (or `*`)
4. (Optional) Add a managed Postgres on Render; Render will provide `DATABASE_URL`.
5. Render will run `pip install -r requirements.txt` and `python manage.py collectstatic` during build. The service start command runs migrations and starts Gunicorn.

Local testing
```powershell
.
venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
cd kingsheralds
python manage.py migrate
python manage.py runserver
```

Notes
- For development on Windows, use the built-in `runserver` or `uvicorn`.
- For production on Render, the Procfile uses Gunicorn and WhiteNoise for static files.
