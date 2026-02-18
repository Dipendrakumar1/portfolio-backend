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
from models import db, Project, Diary, DiarySection, DiaryBullet, Certificate, About, Blog, HomeCard, User, Experience, Skill, Interest, Tool, Language, Achievement, ProjectsPage, BlogsPage, DiaryPage

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
CORS(app)

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

# --- Admin Views with Categories ---
admin = Admin(app, name="Portfolio Dashboard", template_mode="bootstrap4", index_view=MyAdminIndexView())
admin.add_view(AboutAdmin(About, name="Manage About Me", category="About Me"))
admin.add_view(BaseModelView(Experience, name="Manage Experience", category="About Me"))
admin.add_view(BaseModelView(Skill, name="Manage Skills", category="About Me"))
admin.add_view(BaseModelView(Interest, name="Manage Interests", category="About Me"))
admin.add_view(BaseModelView(Tool, name="Manage Tools", category="About Me"))
admin.add_view(BaseModelView(Language, name="Manage Languages", category="About Me"))
admin.add_view(BaseModelView(Achievement, name="Manage Achievements", category="About Me"))
admin.add_view(BaseModelView(Certificate, name="Manage Certificates", category="About Me"))

admin.add_view(BaseModelView(ProjectsPage, name="Page Settings", category="Projects"))
admin.add_view(ProjectAdmin(Project, name="Manage Projects", category="Projects"))

admin.add_view(BaseModelView(BlogsPage, name="Page Settings", category="Blogs"))
admin.add_view(BlogAdmin(Blog, name="Manage Blogs", category="Blogs"))

admin.add_view(BaseModelView(DiaryPage, name="Page Settings", category="My Diary"))
admin.add_view(DiaryAdmin(Diary, name="Manage My Diary", category="My Diary"))

admin.add_view(BaseModelView(HomeCard, name="Manage Home Cards", category="General"))

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
        "order": p.order
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
        "order": c.order
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
        "order": b.order
    }

def about_to_dict(a):
    return {
        "id": str(a.id),
        "title": a.title,
        "body": a.body,
        "hero_image": a.hero_image,
        "skills": [skill_to_dict(s) for s in Skill.objects.order_by("order")],
        "interests": [interest_to_dict(i) for i in Interest.objects.order_by("order")],
        "tools": [tool_to_dict(t) for t in Tool.objects.order_by("order")],
        "languages": [language_to_dict(l) for l in Language.objects.order_by("order")],
        "achievements": [achievement_to_dict(xc) for xc in Achievement.objects.order_by("order")],
        "experiences": [experience_to_dict(e) for e in Experience.objects.order_by("order")],
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

def skill_to_dict(s):
    return {
        "id": str(s.id),
        "name": s.name,
        "category": s.category,
        "level": s.level,
        "order": s.order
    }

def interest_to_dict(i):
    return {
        "id": str(i.id),
        "name": i.name,
        "order": i.order
    }

def tool_to_dict(t):
    return {
        "id": str(t.id),
        "name": t.name,
        "icon_url": t.icon_url,
        "order": t.order
    }

def language_to_dict(l):
    return {
        "id": str(l.id),
        "name": l.name,
        "level": l.level,
        "order": l.order
    }

def achievement_to_dict(a):
    return {
        "id": str(a.id),
        "title": a.title,
        "description": a.description,
        "date": a.date.isoformat() if a.date else None,
        "order": a.order
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
    projects = Project.objects.all().order_by("order")
    return jsonify([project_to_dict(p) for p in projects])

@app.route("/api/projects/meta")
def api_projects_meta():
    page = ProjectsPage.objects.first()
    if not page: return jsonify({})
    return jsonify({"title": page.title, "description": page.description, "hero_image": page.hero_image})

@app.route("/api/diaries")
def api_diaries():
    diaries = Diary.objects.all().order_by("-date")
    return jsonify([diary_list_to_dict(d) for d in diaries])

@app.route("/api/diaries/meta")
def api_diaries_meta():
    page = DiaryPage.objects.first()
    if not page: return jsonify({})
    return jsonify({"title": page.title, "description": page.description, "hero_image": page.hero_image})

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
    blogs = Blog.objects.all().order_by("-published_at")
    return jsonify([blog_to_dict(b) for b in blogs])

@app.route("/api/blogs/meta")
def api_blogs_meta():
    page = BlogsPage.objects.first()
    if not page: return jsonify({})
    return jsonify({"title": page.title, "description": page.description, "hero_image": page.hero_image})

@app.route("/api/home-cards")
def api_home_cards():
    cards = HomeCard.objects.order_by("order")
    return jsonify([home_card_to_dict(c) for c in cards])

@app.route("/api/experiences")
def api_experiences():
    experiences = Experience.objects.order_by("order")
    return jsonify([experience_to_dict(e) for e in experiences])

@app.route("/api/skills")
def api_skills():
    skills = Skill.objects.order_by("order")
    return jsonify([skill_to_dict(s) for s in skills])

@app.route("/api/interests")
def api_interests():
    interests = Interest.objects.order_by("order")
    return jsonify([interest_to_dict(i) for i in interests])

@app.route("/api/tools")
def api_tools():
    tools = Tool.objects.order_by("order")
    return jsonify([tool_to_dict(t) for t in tools])

@app.route("/api/languages")
def api_languages():
    languages = Language.objects.order_by("order")
    return jsonify([language_to_dict(l) for l in languages])
    
@app.route("/api/achievements")
def api_achievements():
    achievements = Achievement.objects.order_by("order")
    return jsonify([achievement_to_dict(a) for a in achievements])

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
