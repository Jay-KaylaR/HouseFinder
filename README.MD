# HouseFinder Mombasa

HouseFinder is a Django-based property listing platform focused on rental/sale listings for Mombasa. It supports property managers, admin approvals, inquiries, and commission tracking.

## Tech Stack
- Python 3.12
- Django 5.x
- SQLite (development)
- Cloudinary (optional) for media storage
- Bootstrap + Font Awesome for frontend

## Quickstart (Development)
1. Create a virtual environment and activate it

```powershell
python -m venv env
.\env\Scripts\Activate.ps1   # PowerShell
# or on Git Bash / macOS/Linux:
# source env/bin/activate
```

2. Install dependencies

```powershell
pip install -r requirements.txt
```

3. Environment variables

Create a `.env` file in the project root or set env vars in your shell. Important variables used by the project:

- `SECRET_KEY` (optional for dev)
- `DEBUG` (True/False)
- `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET` (if using Cloudinary)
- `MPESA_CONSUMER_KEY`, `MPESA_CONSUMER_SECRET`, `MPESA_SHORTCODE`, `MPESA_PASSKEY`, `CALLBACK_URL` (optional)
- `GOOGLE_MAPS_API_KEY` (optional — used on property detail pages)

4. Database migrations

```powershell
python manage.py makemigrations
python manage.py migrate
```

5. Create a superuser

```powershell
python manage.py createsuperuser
```

6. Run the development server

```powershell
python manage.py runserver
# Visit http://127.0.0.1:8000/
```

## Admin & Approvals
- Admins access the admin UI at `/admin/` and the custom admin dashboard at `/managerial/dashboard/`.
- New properties created by managers are saved with `workflow_status='pending'` and `approved=False`.
- Admins can approve or reject properties from the admin dashboard or using the Django admin. Approved properties become public.
- Managers can preview their own (unapproved) listings by visiting the property URL while logged in.

## Files & Important Paths
- Project settings: `HouseFinder/HouseFinder/settings.py`
- Properties app: `HouseFinder/properties/`
- Managerial (admin dashboard): `HouseFinder/managerial/`
- Templates: `HouseFinder/templates/`

## Common Commands
- Run tests (if any):

```powershell
python manage.py test
```

- Collect static files (production):

```powershell
python manage.py collectstatic
```

## Troubleshooting
- CSRF errors: ensure `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` include `127.0.0.1:8000` if you access via that host, clear cookies and re-login.
- Git push error `src refspec master does not match any`: create an initial commit and push. Example:

```bash
git add .
git commit -m "Initial commit"
git branch -M main
git push -u origin main
```

## Contributing
- Fork the repo, make a feature branch, and open a pull request.

## License
MIT — see LICENSE file if included.

---

If you'd like a shorter README or one tailored for production deployment (Docker, Gunicorn, nginx), tell me which format you prefer and I'll generate it.