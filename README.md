# Digital Hub Marketplace

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
python app.py

# 3. Open browser
http://localhost:5000
```

## Admin Panel
- URL: http://localhost:5000/admin/login
- Password: **67**

## Deploy to Render / Railway (Free)

**Render.com:**
1. Push to GitHub
2. New Web Service → connect repo
3. Build: `pip install -r requirements.txt`
4. Start: `gunicorn app:app`
5. Done — free URL!

Add `gunicorn` to requirements.txt for production:
```
flask>=3.0.0
werkzeug>=3.0.0
gunicorn>=21.0.0
```

## Features
- 🛍️ Product listing with search, filter, sort
- 🛒 Cart (session-based) with drawer + cart page
- 🔐 Password-protected admin panel (pw: 67)
- ➕ Add / ✏️ Edit / 🗑️ Delete products
- 🖼️ Custom icon upload per product (drag & drop)
- 🌐 Live site settings (name, colors, hero text, footer)
- 📊 Analytics (top products, category breakdown, revenue)
- 💾 Data saved to data.json (persistent)

## File Structure
```
digitalhub/
├── app.py              # Flask app (all routes)
├── data.json           # Auto-created on first run
├── requirements.txt
├── static/
│   └── uploads/        # Uploaded product icons
└── templates/
    ├── base.html       # Store base (nav, cart drawer)
    ├── index.html      # Homepage / product listing
    ├── cart.html       # Cart page
    ├── admin_login.html
    ├── admin_base.html # Admin layout
    ├── admin_products.html
    ├── admin_product_form.html  # Add/Edit form
    ├── admin_site.html
    └── admin_analytics.html
```
