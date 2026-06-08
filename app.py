from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import json, os, uuid
from functools import wraps
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "digitalhub_secret_2025"

ADMIN_PASSWORD = "67"
DATA_FILE = "data.json"
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "svg", "webp"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5MB

# ── Data helpers ──────────────────────────────────────────────────────────────
DEFAULT_DATA = {
    "site": {
        "name": "Digital Hub",
        "tagline": "Premium digital products for creators & developers",
        "primaryColor": "#6C3EE8",
        "accentColor": "#F59E0B",
        "heroTitle": "Unlock Your Creative Potential",
        "heroSubtitle": "Discover thousands of premium templates, icons, fonts, and tools",
        "currency": "USD",
        "footerText": "© 2025 Digital Hub. All rights reserved."
    },
    "products": [
        {"id": "1", "name": "Pro UI Kit", "category": "UI Kits", "price": 49, "orig": 79, "image": "🎨", "icon": "", "desc": "500+ components for Figma & React. Dark/light mode. Fully responsive.", "rating": 4.8, "sales": 1240, "featured": True, "tags": ["figma", "react", "components"]},
        {"id": "2", "name": "Icon Pack Ultra", "category": "Icons", "price": 19, "orig": 29, "image": "⚡", "icon": "", "desc": "3000+ hand-crafted SVG icons in multiple styles. Free updates forever.", "rating": 4.9, "sales": 3410, "featured": True, "tags": ["svg", "icons", "design"]},
        {"id": "3", "name": "Landing Page Bundle", "category": "Templates", "price": 89, "orig": 149, "image": "🚀", "icon": "", "desc": "20 stunning landing page templates. HTML, React & Next.js versions included.", "rating": 4.7, "sales": 890, "featured": False, "tags": ["html", "nextjs", "landing"]},
        {"id": "4", "name": "Font Collection", "category": "Fonts", "price": 29, "orig": 49, "image": "✍️", "icon": "", "desc": "45 premium display & body fonts. Commercial license included.", "rating": 4.6, "sales": 2100, "featured": False, "tags": ["fonts", "typography", "commercial"]},
        {"id": "5", "name": "Dashboard Pro", "category": "UI Kits", "price": 69, "orig": 99, "image": "📊", "icon": "", "desc": "Admin dashboard template with 80+ pages. React + Tailwind CSS.", "rating": 4.9, "sales": 670, "featured": True, "tags": ["dashboard", "admin", "tailwind"]},
        {"id": "6", "name": "Motion Graphics Pack", "category": "Templates", "price": 39, "orig": 59, "image": "🎬", "icon": "", "desc": "100+ After Effects & Lottie animations for your projects.", "rating": 4.5, "sales": 450, "featured": False, "tags": ["animation", "lottie", "motion"]},
        {"id": "7", "name": "E-Commerce Kit", "category": "Templates", "price": 99, "orig": 159, "image": "🛒", "icon": "", "desc": "Complete e-commerce UI with cart, checkout, and product pages.", "rating": 4.8, "sales": 320, "featured": False, "tags": ["ecommerce", "shop", "checkout"]},
        {"id": "8", "name": "3D Asset Library", "category": "3D Assets", "price": 59, "orig": 89, "image": "🧊", "icon": "", "desc": "500+ 3D illustrations and assets. Blender, OBJ, and PNG formats.", "rating": 4.7, "sales": 780, "featured": True, "tags": ["3d", "blender", "illustrations"]},
    ]
}

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return DEFAULT_DATA.copy()

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# ── Auth decorator ────────────────────────────────────────────────────────────
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated

# ── Store routes ──────────────────────────────────────────────────────────────
@app.route("/")
def index():
    data = load_data()
    products = data["products"]
    cat = request.args.get("cat", "All")
    srch = request.args.get("q", "")
    sort = request.args.get("sort", "featured")

    if cat != "All":
        products = [p for p in products if p["category"] == cat]
    if srch:
        sl = srch.lower()
        products = [p for p in products if sl in p["name"].lower() or sl in p["desc"].lower() or any(sl in t for t in p["tags"])]
    if sort == "featured":
        products = sorted(products, key=lambda p: (0 if p["featured"] else 1))
    elif sort == "price_asc":
        products = sorted(products, key=lambda p: p["price"])
    elif sort == "price_desc":
        products = sorted(products, key=lambda p: -p["price"])
    elif sort == "rating":
        products = sorted(products, key=lambda p: -p["rating"])
    elif sort == "popular":
        products = sorted(products, key=lambda p: -p["sales"])

    categories = ["All", "UI Kits", "Icons", "Templates", "Fonts", "3D Assets"]
    cat_colors = {"UI Kits": "#6C3EE8", "Icons": "#F59E0B", "Templates": "#10B981", "Fonts": "#EF4444", "3D Assets": "#3B82F6"}
    all_products = load_data()["products"]
    total_sales = sum(p["sales"] for p in all_products)

    return render_template("index.html",
        site=data["site"],
        products=products,
        all_products=all_products,
        categories=categories,
        cat_colors=cat_colors,
        selected_cat=cat,
        search=srch,
        sort=sort,
        total_sales=total_sales
    )

# ── Cart (session-based) ──────────────────────────────────────────────────────
@app.route("/cart/add/<pid>", methods=["POST"])
def cart_add(pid):
    cart = session.get("cart", {})
    data = load_data()
    prod = next((p for p in data["products"] if p["id"] == pid), None)
    if prod:
        if pid in cart:
            cart[pid]["qty"] += 1
        else:
            cart[pid] = {"qty": 1, **prod}
    session["cart"] = cart
    return jsonify({"ok": True, "count": sum(i["qty"] for i in cart.values())})

@app.route("/cart/remove/<pid>", methods=["POST"])
def cart_remove(pid):
    cart = session.get("cart", {})
    cart.pop(pid, None)
    session["cart"] = cart
    return jsonify({"ok": True, "count": sum(i["qty"] for i in cart.values())})

@app.route("/cart/update/<pid>", methods=["POST"])
def cart_update(pid):
    qty = int(request.json.get("qty", 1))
    cart = session.get("cart", {})
    if pid in cart:
        if qty <= 0:
            del cart[pid]
        else:
            cart[pid]["qty"] = qty
    session["cart"] = cart
    total = sum(i["price"] * i["qty"] for i in cart.values())
    count = sum(i["qty"] for i in cart.values())
    return jsonify({"ok": True, "count": count, "total": total})

@app.route("/cart")
def cart_view():
    cart = session.get("cart", {})
    data = load_data()
    total = sum(i["price"] * i["qty"] for i in cart.values())
    return render_template("cart.html", site=data["site"], cart=cart, total=total)

# ── Admin: Login ──────────────────────────────────────────────────────────────
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    error = False
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("admin_products"))
        error = True
    data = load_data()
    return render_template("admin_login.html", site=data["site"], error=error)

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("index"))

# ── Admin: Products ───────────────────────────────────────────────────────────
@app.route("/admin/products")
@admin_required
def admin_products():
    data = load_data()
    srch = request.args.get("q", "")
    products = data["products"]
    if srch:
        sl = srch.lower()
        products = [p for p in products if sl in p["name"].lower() or sl in p["category"].lower()]
    cat_colors = {"UI Kits": "#6C3EE8", "Icons": "#F59E0B", "Templates": "#10B981", "Fonts": "#EF4444", "3D Assets": "#3B82F6"}
    total_sales = sum(p["sales"] for p in data["products"])
    return render_template("admin_products.html",
        site=data["site"], products=products, all_products=data["products"],
        cat_colors=cat_colors, search=srch, total_sales=total_sales)

@app.route("/admin/products/add", methods=["GET", "POST"])
@admin_required
def admin_add_product():
    data = load_data()
    categories = ["UI Kits", "Icons", "Templates", "Fonts", "3D Assets"]
    emojis = ["🎨", "⚡", "🚀", "✍️", "📊", "🎬", "🛒", "🧊", "🎯", "💎", "🌈", "🔥", "💡", "🎁", "📱"]
    if request.method == "POST":
        icon_path = ""
        if "icon_file" in request.files:
            f = request.files["icon_file"]
            if f and f.filename and allowed_file(f.filename):
                ext = f.filename.rsplit(".", 1)[1].lower()
                fname = str(uuid.uuid4()) + "." + ext
                f.save(os.path.join(app.config["UPLOAD_FOLDER"], fname))
                icon_path = "/static/uploads/" + fname
        tags = [t.strip() for t in request.form.get("tags", "").split(",") if t.strip()]
        prod = {
            "id": str(uuid.uuid4()),
            "name": request.form["name"],
            "category": request.form["category"],
            "price": int(request.form.get("price", 0)),
            "orig": int(request.form.get("orig", 0)),
            "image": request.form.get("image", "🎨"),
            "icon": icon_path,
            "desc": request.form.get("desc", ""),
            "rating": float(request.form.get("rating", 4.5)),
            "sales": int(request.form.get("sales", 0)),
            "featured": "featured" in request.form,
            "tags": tags,
        }
        data["products"].append(prod)
        save_data(data)
        flash("✅ Product added!", "success")
        return redirect(url_for("admin_products"))
    return render_template("admin_product_form.html", site=data["site"], product=None, categories=categories, emojis=emojis, action="Add")

@app.route("/admin/products/edit/<pid>", methods=["GET", "POST"])
@admin_required
def admin_edit_product(pid):
    data = load_data()
    prod = next((p for p in data["products"] if p["id"] == pid), None)
    if not prod:
        return redirect(url_for("admin_products"))
    categories = ["UI Kits", "Icons", "Templates", "Fonts", "3D Assets"]
    emojis = ["🎨", "⚡", "🚀", "✍️", "📊", "🎬", "🛒", "🧊", "🎯", "💎", "🌈", "🔥", "💡", "🎁", "📱"]
    if request.method == "POST":
        icon_path = prod.get("icon", "")
        if "icon_file" in request.files:
            f = request.files["icon_file"]
            if f and f.filename and allowed_file(f.filename):
                ext = f.filename.rsplit(".", 1)[1].lower()
                fname = str(uuid.uuid4()) + "." + ext
                f.save(os.path.join(app.config["UPLOAD_FOLDER"], fname))
                icon_path = "/static/uploads/" + fname
        if request.form.get("remove_icon"):
            icon_path = ""
        tags = [t.strip() for t in request.form.get("tags", "").split(",") if t.strip()]
        prod.update({
            "name": request.form["name"],
            "category": request.form["category"],
            "price": int(request.form.get("price", 0)),
            "orig": int(request.form.get("orig", 0)),
            "image": request.form.get("image", prod["image"]),
            "icon": icon_path,
            "desc": request.form.get("desc", ""),
            "rating": float(request.form.get("rating", 4.5)),
            "sales": int(request.form.get("sales", 0)),
            "featured": "featured" in request.form,
            "tags": tags,
        })
        save_data(data)
        flash("✅ Product updated!", "success")
        return redirect(url_for("admin_products"))
    return render_template("admin_product_form.html", site=data["site"], product=prod, categories=categories, emojis=emojis, action="Edit")

@app.route("/admin/products/delete/<pid>", methods=["POST"])
@admin_required
def admin_delete_product(pid):
    data = load_data()
    data["products"] = [p for p in data["products"] if p["id"] != pid]
    save_data(data)
    flash("🗑️ Product deleted", "info")
    return redirect(url_for("admin_products"))

# ── Admin: Site Settings ──────────────────────────────────────────────────────
@app.route("/admin/site", methods=["GET", "POST"])
@admin_required
def admin_site():
    data = load_data()
    if request.method == "POST":
        data["site"].update({
            "name": request.form.get("name", data["site"]["name"]),
            "tagline": request.form.get("tagline", ""),
            "primaryColor": request.form.get("primaryColor", "#6C3EE8"),
            "accentColor": request.form.get("accentColor", "#F59E0B"),
            "heroTitle": request.form.get("heroTitle", ""),
            "heroSubtitle": request.form.get("heroSubtitle", ""),
            "currency": request.form.get("currency", "USD"),
            "footerText": request.form.get("footerText", ""),
        })
        save_data(data)
        flash("✅ Site settings saved!", "success")
        return redirect(url_for("admin_site"))
    return render_template("admin_site.html", site=data["site"])

# ── Admin: Analytics ──────────────────────────────────────────────────────────
@app.route("/admin/analytics")
@admin_required
def admin_analytics():
    data = load_data()
    products = data["products"]
    total_sales = sum(p["sales"] for p in products)
    total_revenue = sum(p["price"] * p["sales"] for p in products)
    avg_price = round(sum(p["price"] for p in products) / max(len(products), 1))
    avg_disc = round(sum((1 - p["price"] / p["orig"]) * 100 for p in products if p["orig"]) / max(len(products), 1))
    top_products = sorted(products, key=lambda p: -p["sales"])[:5]
    cat_sales = {}
    for p in products:
        cat_sales[p["category"]] = cat_sales.get(p["category"], 0) + p["sales"]
    cat_pcts = {k: round(v / max(total_sales, 1) * 100) for k, v in cat_sales.items()}
    cat_colors = {"UI Kits": "#6C3EE8", "Icons": "#F59E0B", "Templates": "#10B981", "Fonts": "#EF4444", "3D Assets": "#3B82F6"}
    top_rated = sorted(products, key=lambda p: -p["rating"])[:5]
    max_sales = max((p["sales"] for p in products), default=1)
    return render_template("admin_analytics.html",
        site=data["site"], products=products,
        total_sales=total_sales, total_revenue=total_revenue,
        avg_price=avg_price, avg_disc=avg_disc,
        top_products=top_products, cat_pcts=cat_pcts,
        cat_colors=cat_colors, top_rated=top_rated,
        max_sales=max_sales
    )

if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True, port=5000)

@app.route("/cart/state")
def cart_state():
    cart = session.get("cart", {})
    return jsonify({"cart": cart})
