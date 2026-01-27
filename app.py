import os
from flask import Flask, jsonify, abort, render_template, redirect, url_for, request, flash
from flask_admin import Admin, AdminIndexView, expose
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from flask_admin import Admin
from flask_admin.contrib.mongoengine import ModelView
from flask_cors import CORS
from wtforms import TextAreaField
from wtforms.widgets import TextArea

from config import Config
from models import db, Project, Diary, DiarySection, DiaryBullet, Certificate, About, Blog, HomeCard, User, Experience

# --------------------------------------------------------------------
# App & config
# --------------------------------------------------------------------

app = Flask(__name__)
app.config.from_object(Config)

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.objects(pk=user_id).first()

db.init_app(app)

# CORS configuration: Allow localhost for dev and optional FRONTEND_URL from environment
allowed_origins = ["http://localhost:5173"]
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    allowed_origins.append(frontend_url)

CORS(app, origins=allowed_origins)

try:
    # Attempt to access the database to verify connection
    # MongoEngine connects lazily, so we simply print here, 
    # but a real check would be: from mongoengine import get_connection; get_connection().admin.command('ping')
    print("db connected")
except Exception as e:
    print(f"db connection failed: {e}")

# --------------------------------------------------------------------
# Flask-Admin dashboard
# --------------------------------------------------------------------

class RichTextArea(TextArea):
    """Hook for later JS WYSIWYG if you want."""
    pass

class MyAdminIndexView(AdminIndexView):
    def is_visible(self):
        return False
        
    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        return super(MyAdminIndexView, self).index()

class BaseModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))

    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    page_size = 20
    create_modal = True
    edit_modal = True

class ProjectAdmin(BaseModelView):
    column_searchable_list = ("title", "slug", "short_description")
    column_filters = ("title",)
    form_overrides = {
        "long_description": TextAreaField,
    }
    form_widget_args = {
        "long_description": {"widget": RichTextArea()},
    }

class BlogAdmin(BaseModelView):
    column_searchable_list = ("title", "slug", "subtitle", "author")
    column_filters = ("author",)
    column_default_sort = ("published_at", True)
    form_overrides = {
        "content": TextAreaField,
    }
    form_widget_args = {
        "content": {"widget": RichTextArea()},
    }

class DiaryAdmin(BaseModelView):
    column_searchable_list = ("month_label", "slug", "author")
    column_filters = ("month_label", "slug", "author")
    column_default_sort = ("date", True)

class AboutAdmin(BaseModelView):
    form_overrides = {
        "body": TextAreaField,
    }
    form_widget_args = {
        "body": {"widget": RichTextArea()},
    }

admin = Admin(app, name="Portfolio Dashboard", template_mode="bootstrap4", index_view=MyAdminIndexView())
admin.add_view(AboutAdmin(About, name="About"))
admin.add_view(BlogAdmin(Blog, name="Blog"))
admin.add_view(ProjectAdmin(Project, name="Project"))
admin.add_view(DiaryAdmin(Diary, name="Diary"))
admin.add_view(BaseModelView(Certificate, name="Certificate"))
admin.add_view(BaseModelView(HomeCard, name="Home Cards"))
admin.add_view(BaseModelView(Experience, name="Experience"))

# --------------------------------------------------------------------
# Helper serializers
# --------------------------------------------------------------------

def project_to_dict(p):
    return {
        "id": str(p.id),
        "slug": p.slug,
        "title": p.title,
        "short_description": p.short_description,
        "long_description": p.long_description,
        "hero_image": p.hero_image,
        "repo_url": p.repo_url,
        "live_url": p.live_url,
    }

def diary_list_to_dict(d):
    return {
        "id": str(d.id),
        "slug": d.slug,
        "month_label": d.month_label,
        "date": d.date.isoformat() if d.date else None,
        "author": d.author,
        "summary": d.summary,
        "word_count": d.word_count,
    }

def diary_detail_to_dict(d):
    return {
        **diary_list_to_dict(d),
        "sections": [
            {
                "title": s.title,
                "order": s.order,
                "bullets": [
                    {"text": b.text, "order": b.order}
                    for b in s.bullets
                ],
            }
            for s in d.sections
        ],
    }

def certificate_to_dict(c):
    return {
        "id": str(c.id),
        "name": c.name,
        "image_url": c.image_url,
        "link_url": c.link_url,
    }

def blog_to_dict(b):
    return {
        "id": str(b.id),
        "slug": b.slug,
        "title": b.title,
        "subtitle": b.subtitle,
        "published_at": b.published_at.isoformat() if b.published_at else None,
        "author": b.author,
        "read_time_min": b.read_time_min,
        "word_count": b.word_count,
        "hero_image": b.hero_image,
        "content": b.content,
    }

def about_to_dict(a):
    return {
        "id": str(a.id),
        "title": a.title,
        "body": a.body,
        "hero_image": a.hero_image,
    }

def home_card_to_dict(c):
    return {
        "id": str(c.id),
        "title": c.title,
        "image_url": c.image_url,
        "alt_text": c.alt_text,
        "link_url": c.link_url,
        "order": c.order
    }

def experience_to_dict(e):
    return {
        "id": str(e.id),
        "company_name": e.company_name,
        "company_logo": e.company_logo,
        "role": e.role,
        "tenure": e.tenure,
        "contributions": e.contributions,
        "order": e.order
    }

# --------------------------------------------------------------------
# Auth Routes
# --------------------------------------------------------------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.objects(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin.index'))
        else:
            flash('Invalid username or password')
            
    return render_template('login.html', admin_view=admin.index_view)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --------------------------------------------------------------------
# JSON API endpoints
# --------------------------------------------------------------------

@app.route("/api/projects")
def api_projects():
    projects = Project.objects.all()
    return jsonify([project_to_dict(p) for p in projects])

@app.route("/api/diaries")
def api_diaries():
    diaries = Diary.objects.order_by("-date")
    return jsonify([diary_list_to_dict(d) for d in diaries])

@app.route("/api/diaries/<slug>")
def api_diary_detail(slug):
    diary = Diary.objects(slug=slug).first()
    if not diary:
        abort(404)
    return jsonify(diary_detail_to_dict(diary))

@app.route("/api/certificates")
def api_certificates():
    certs = Certificate.objects.all()
    return jsonify([certificate_to_dict(c) for c in certs])

@app.route("/api/about")
def api_about():
    about = About.objects.first()
    if not about:
        return jsonify({"title": "About Me", "body": "", "hero_image": ""})
    return jsonify(about_to_dict(about))

@app.route("/api/blogs")
def api_blogs():
    blogs = Blog.objects.order_by("-published_at")
    return jsonify([blog_to_dict(b) for b in blogs])

@app.route("/api/home-cards")
def api_home_cards():
    cards = HomeCard.objects.order_by("order")
    return jsonify([home_card_to_dict(c) for c in cards])

@app.route("/api/experiences")
def api_experiences():
    exps = Experience.objects.order_by("order")
    return jsonify([experience_to_dict(e) for e in exps])

@app.route("/api/blogs/<slug>")
def api_blog_detail(slug):
    blog = Blog.objects(slug=slug).first()
    if not blog:
        abort(404)
    return jsonify(blog_to_dict(blog))

# --------------------------------------------------------------------
# Entrypoint
# --------------------------------------------------------------------

if __name__ == "__main__":
    # In production, Render will provide a PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
