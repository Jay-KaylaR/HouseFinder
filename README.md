# user roles
Renter/Buyer: Browse, save favorites, send inquiries
Property Manager: List properties, manage inquiries, pay commissions via M-Pesa
Administrator: Verify listings/users, track commissions, analytics


django-admin startproject housefinder
cd housefinder
python manage.py startapp accounts main properties manage
pip install django cloudinary django-cloudinary-storage django-mpesa python-decouple pillow


python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
python manage.py runserver

# In UserRegistrationForm
user_type = forms.ChoiceField(choices=User.USER_TYPE_CHOICES, ...)
Run Commands


python manage.py makemigrations accounts --empty  # If model changes
python manage.py migrate
python manage.py createsuperuser


python manage.py makemigrations accounts
python manage.py migrate


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # For testing
# For production: use SMTP settings


URL Examples:
text
GET /properties/                          → listings_view (public listings)
GET /properties/nyali-apartment/          → property_detail_view (property page)
POST /properties/create/                  → create_property_view (managers only)
GET /properties/5/edit/                   → edit_property_view (own properties)
POST /properties/5/delete/                → delete_property_view
GET /properties/my-properties/            → my_properties_view (manager dashboard)
POST /properties/5/inquiry/               → send_inquiry_view (renters contact managers)

# 1. Create project folder
mkdir housefinder-mombasa && cd housefinder-mombasa

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate    # Windows

# 3. Copy ALL files above into correct folders
# (Use the generated code from our conversation)

# 4. Install & Run
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver


1. Clone & Install
bash
git clone <your-repo>
cd housefinder
pip install -r requirements.txt
2. Environment Setup
Create .env file:

bash
cp .env.example .env
Required:

text
SECRET_KEY=your-secret-key
DEBUG=True
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_secret
MPESA_CONSUMER_KEY=your_mpesa_key
MPESA_CONSUMER_SECRET=your_mpesa_secret
MPESA_SHORTCODE=174379
MPESA_PASSKEY=your_passkey
CALLBACK_URL=https://yourdomain.com/manage/callback/
3. Database & Migrations
bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
4. Static Files
bash
python manage.py collectstatic --noinput
5. Run Server
bash
python manage.py runserver
Visit: http://localhost:8000

📱 Demo URLs
Role	URL	Description
Public	/	Homepage (featured properties)
Public	/properties/	All listings + filters
Public	/properties/nyali-apartment/	Property detail
User	/accounts/register/	Create account
Manager	/properties/create/	Add new property
Manager	/properties/my-properties/	My listings
Admin	/admin/	Django admin
Admin	/manage/dashboard/	Analytics dashboard
🛠 Key Integrations
Cloudinary (Media Storage)
text
- Property images (unlimited)
- Profile photos
- National ID verification
- Auto-optimized CDN delivery
M-Pesa Daraja API (Payments)
text
1. Manager creates property → 10% commission calculated
2. Property rented → Manager pays via STK Push
3. Callback updates payment status
4. Admin tracks earnings
Google Maps
text
- Property lat/lng coordinates
- Interactive map view
- Radius search (future)
👥 User Roles & Permissions
python
# accounts/models.py
USER_TYPE_CHOICES = [
    ('renter', 'Renter/Buyer'),     # Browse + inquire
    ('manager', 'Property Manager'), # CRUD properties + M-Pesa
    ('admin', 'Administrator'),     # Verify + analytics
]
📊 Admin Dashboard Stats
text
✅ Total Properties
✅ Pending Approvals  
✅ Monthly Commissions
✅ Verified Managers
✅ Active Users
✅ Property Views
🏗 Tech Stack
Layer	Technology
Backend	Django 5.1, Python 3.11
Database	SQLite (dev), PostgreSQL (prod)
Frontend	Bootstrap 5.3, Font Awesome 6
Media	Cloudinary CDN
Payments	M-Pesa Daraja API
Maps	Google Maps JavaScript API
Deployment	Docker, Railway, Heroku, Render
🚀 Deployment
Production Checklist
bash
# 1. Environment
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
DATABASE_URL=postgresql://...

# 2. Migrations
python manage.py migrate

# 3. Static Files
python manage.py collectstatic --noinput

# 4. M-Pesa Sandbox
ngrok http 8000  # For callback testing
Docker (Optional)
text
FROM python:3.11-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD python manage.py migrate && python manage.py runserver 0.0.0.0:8000
📱 Mobile-First Design
Fully Responsive - Mobile, tablet, desktop

PWA Ready - Installable web app

Fast Loading - Cloudinary optimization

Touch Optimized - Swipe galleries, map interactions

🔒 Security Features
text
✅ Password reset (email)
✅ National ID verification
✅ Manager KRA PIN check
✅ Property approval workflow
✅ CSRF protection
✅ Rate limiting ready
✅ Admin audit logs (future)
🤝 Contributing
Fork the repository

Create feature branch (git checkout -b feature/property-reviews)

Commit changes (git commit -m 'Add property reviews')

Push (git push origin feature/property-reviews)

Open Pull Request

📄 License
MIT License - See LICENSE file.

📞 Contact
HouseFinder Mombasa
✉️ support@housefindermombasa.co.ke
📞 +254 712 345 678

[
[
[

Built with ❤️ for Mombasa residents | © 2025 HouseFinder Mombasa
