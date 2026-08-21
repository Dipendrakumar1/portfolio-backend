import os
from flask import Flask, jsonify, abort, render_template, redirect, url_for, request, flash, Response
from flask_admin import Admin, AdminIndexView, expose
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from flask_admin.contrib.mongoengine import ModelView
from flask_cors import CORS
from wtforms import TextAreaField
from wtforms.widgets import TextArea
from html import escape

from config import Config
from models import db, Project, Diary, DiarySection, DiaryBullet, Certificate, About, Blog, HomeCard, User, Experience, Skill, Interest, Tool, Language, Achievement, ProjectsPage, BlogsPage, DiaryPage, VisitEvent, LikeEvent, ContactMessage
from datetime import datetime, timedelta, timezone
import pytz
import requests
from flask_admin import BaseView

# --------------------------------------------------------------------
# App & config
# --------------------------------------------------------------------

app = Flask(__name__)
app.config.from_object(Config)

# Validate required environment variables
Config.validate()

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Access Denied. Please login first."
login_manager.login_message_category = "warning"

@login_manager.user_loader
def load_user(user_id):
    return User.objects(pk=user_id).first()

db.init_app(app)

# CORS configuration: Restrict to specific origins
frontend_url = os.getenv("FRONTEND_URL", "https://www.dipendrakumaryadav.com.np")
CORS(app, origins=[frontend_url])

try:
    # Attempt to access the database to verify connection
    # MongoEngine connects lazily, so we simply print here, 
    # but a real check would be: from mongoengine import get_connection; get_connection().admin.command('ping')
    print("db connected")
except Exception as e:
    print(f"db connection failed: {e}")

@app.before_request
def protect_admin():
    if request.path.startswith('/admin') and not current_user.is_authenticated:
        if request.endpoint != 'login' and request.path != '/login':
            flash('Access Denied. Please login first.')
            return redirect(url_for('login', next=request.url))

# --------------------------------------------------------------------
# Flask-Admin dashboard
# --------------------------------------------------------------------

class RichTextArea(TextArea):
    """Hook for later JS WYSIWYG if you want."""
    pass

class MyAdminIndexView(AdminIndexView):
    def is_visible(self):
        return False
        
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        flash('Access Denied. Please login first.', 'warning')
        return redirect(url_for('login', next=request.url))

    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            flash('Access Denied. Please login first.')
            return redirect(url_for('login', next=request.url))
        return super(MyAdminIndexView, self).index()

class BaseModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        flash('Access Denied. Please login first.')
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
    column_filters = ("title", "category")
    column_choices = {
        "category": [("Real Client", "Real Client"), ("Personal", "Personal")],
    }
    column_exclude_list = ("long_description",)
    create_modal = False
    edit_modal = False
    form_overrides = {
        "long_description": TextAreaField,
    }
    form_widget_args = {
        "long_description": {
            "class": "quill-editor",
        },
    }

class BlogAdmin(BaseModelView):
    column_searchable_list = ("title", "slug", "subtitle", "author")
    column_filters = ("author",)
    column_default_sort = ("published_at", True)
    column_exclude_list = ("content",)
    create_modal = False
    edit_modal = False
    form_overrides = {
        "content": TextAreaField,
    }
    form_widget_args = {
        "content": {
            "class": "quill-editor",
        },
    }

class DiaryAdmin(BaseModelView):
    column_searchable_list = ("month_label", "slug", "author")
    column_filters = ("month_label", "slug", "author")
    column_default_sort = ("date", True)
    column_exclude_list = ("summary", "sections")
    create_modal = False
    edit_modal = False
    form_overrides = {
        "summary": TextAreaField,
    }
    form_widget_args = {
        "summary": {
            "class": "quill-editor",
        },
    }

class PageSettingsAdmin(BaseModelView):
    create_modal = False
    edit_modal = False
    form_overrides = {
        "description": TextAreaField,
    }
    form_widget_args = {
        "description": {
            "class": "quill-editor",
        },
    }

class AboutAdmin(BaseModelView):
    form_overrides = {
        "body": TextAreaField,
    }
    form_widget_args = {
        "body": {
            "class": "quill-editor",
        },
    }

# --- Custom Analytics View ---
class AnalyticsView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        flash('Access Denied. Please login first.')
        return redirect(url_for('login', next=request.url))

    @expose('/')
    def index(self):
        # Get total visits
        total_visits_count = VisitEvent.objects.count()

        # Get unique visitors
        unique_sessions = VisitEvent.objects.distinct('session_id')
        unique_visitors_count = len(unique_sessions)

        # Get average scroll depth
        pipeline_scroll = [
            {"$group": {"_id": "$session_id", "max_scroll": {"$max": "$scroll_depth"}}},
            {"$group": {"_id": None, "avg_scroll": {"$avg": "$max_scroll"}}}
        ]
        scroll_result = list(VisitEvent.objects.aggregate(*pipeline_scroll))
        avg_scroll_depth = round(scroll_result[0]['avg_scroll'], 1) if scroll_result and scroll_result[0].get('avg_scroll') is not None else 0

        # Calculate dates for charts
        today = datetime.now(pytz.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Daily visits (last 7 days by day)
        daily_labels = []
        daily_data = []
        for i in range(6, -1, -1):
            day_start = today - timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            daily_labels.append(day_start.strftime("%b %d"))
            daily_data.append(VisitEvent.objects(timestamp__gte=day_start, timestamp__lt=day_end).count())

        # Monthly visits (last 6 months)
        monthly_labels = []
        monthly_data = []
        for i in range(5, -1, -1):
            month_start = today - timedelta(days=30*i)
            month_start = month_start.replace(day=1)
            if i == 0:
                month_end = today + timedelta(days=32)
                month_end = month_end.replace(day=1)
            else:
                month_end = today - timedelta(days=30*(i-1))
                month_end = month_end.replace(day=1)
            monthly_labels.append(month_start.strftime("%b %Y"))
            monthly_data.append(VisitEvent.objects(timestamp__gte=month_start, timestamp__lt=month_end).count())

        # Top pages
        pipeline_pages = [
            {"$group": {"_id": "$path", "views": {"$sum": 1}}},
            {"$sort": {"views": -1}},
            {"$limit": 10}
        ]
        top_pages = list(VisitEvent.objects.aggregate(*pipeline_pages))
        top_pages_data = [{"path": p["_id"], "views": p["views"]} for p in top_pages]

        # Blog Likes
        pipeline_likes = [
            {"$group": {"_id": "$blog_slug", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        blog_likes = list(LikeEvent.objects.aggregate(*pipeline_likes))
        blog_likes_data = [{"slug": l["_id"], "count": l["count"]} for l in blog_likes]

        # Traffic Sources / Referrers Breakdown
        pipeline_sources = [
            {"$group": {"_id": {"$ifNull": ["$referrer", "Direct / Bookmark"]}, "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 8}
        ]
        traffic_sources_raw = list(VisitEvent.objects.aggregate(*pipeline_sources))
        traffic_sources = [{"name": s["_id"] or "Direct / Bookmark", "count": s["count"]} for s in traffic_sources_raw]

        # Devices Breakdown
        pipeline_devices = [
            {"$group": {"_id": {"$ifNull": ["$device_type", "Desktop"]}, "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        device_stats = [{"name": d["_id"] or "Desktop", "count": d["count"]} for d in list(VisitEvent.objects.aggregate(*pipeline_devices))]

        # Operating Systems Breakdown
        pipeline_os = [
            {"$group": {"_id": {"$ifNull": ["$os", "Unknown"]}, "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 6}
        ]
        os_stats = [{"name": o["_id"] or "Unknown", "count": o["count"]} for o in list(VisitEvent.objects.aggregate(*pipeline_os))]

        # High-Intent Recruiter Leads Count (Sessions who visited /hire-me or /aboutme)
        recruiter_sessions = VisitEvent.objects(path__in=["/hire-me", "/aboutme"]).distinct("session_id")
        recruiter_leads_count = len(recruiter_sessions)

        # Recent Visitor & Recruiter Journeys (Grouped by Session ID)
        pipeline_journeys = [
            {
                "$sort": {"timestamp": -1}
            },
            {
                "$group": {
                    "_id": "$session_id",
                    "paths": {"$addToSet": "$path"},
                    "max_scroll": {"$max": "$scroll_depth"},
                    "ip_address": {"$first": "$ip_address"},
                    "device_type": {"$first": "$device_type"},
                    "browser": {"$first": "$browser"},
                    "os": {"$first": "$os"},
                    "referrer": {"$first": "$referrer"},
                    "screen_resolution": {"$first": "$screen_resolution"},
                    "last_seen": {"$max": "$timestamp"},
                    "interactions_count": {"$sum": 1}
                }
            },
            {
                "$sort": {"last_seen": -1}
            },
            {
                "$limit": 25
            }
        ]
        recent_journeys_raw = list(VisitEvent.objects.aggregate(*pipeline_journeys))
        recent_journeys = []
        for j in recent_journeys_raw:
            paths = j.get("paths", [])
            max_scroll = j.get("max_scroll", 0)
            
            # Determine interest tier
            is_hire = any("/hire-me" in str(p) for p in paths)
            is_about = any("/aboutme" in str(p) for p in paths)
            is_projects = any("/projects" in str(p) for p in paths)
            
            if is_hire or (is_about and max_scroll >= 50):
                interest_badge = "🔥 High Recruiter Interest"
                interest_class = "badge-danger"
            elif is_projects or len(paths) >= 3 or max_scroll >= 60:
                interest_badge = "⭐ Engaged Explorer"
                interest_class = "badge-primary"
            else:
                interest_badge = "👤 Casual Visitor"
                interest_class = "badge-secondary"

            recent_journeys.append({
                "session_id": (j["_id"] or "")[:12] + "...",
                "full_session_id": j["_id"],
                "ip_address": j.get("ip_address") or "Private / Proxy",
                "device_type": j.get("device_type") or "Desktop",
                "os": j.get("os") or "Unknown",
                "browser": j.get("browser") or "Browser",
                "screen_resolution": j.get("screen_resolution") or "N/A",
                "referrer": j.get("referrer") or "Direct",
                "paths": paths,
                "max_scroll": max_scroll,
                "interactions_count": j.get("interactions_count", 1),
                "last_seen": j["last_seen"].strftime("%b %d, %H:%M UTC") if j.get("last_seen") else "Just now",
                "interest_badge": interest_badge,
                "interest_class": interest_class
            })

        return self.render('admin/analytics.html', 
                           total_visits=total_visits_count,
                           unique_visitors=unique_visitors_count,
                           avg_scroll_depth=avg_scroll_depth,
                           recruiter_leads_count=recruiter_leads_count,
                           daily_labels=daily_labels,
                           daily_data=daily_data,
                           monthly_labels=monthly_labels,
                           monthly_data=monthly_data,
                           top_pages=top_pages_data,
                           blog_likes=blog_likes_data,
                           traffic_sources=traffic_sources,
                           device_stats=device_stats,
                           os_stats=os_stats,
                           recent_journeys=recent_journeys)

from flask_admin.menu import MenuLink

# --- Admin Views with Categories ---
admin = Admin(app, name="Portfolio Dashboard", template_mode="bootstrap4", index_view=MyAdminIndexView())

# Add Logout Link
admin.add_link(MenuLink(name='Logout', category='', url='/logout'))

admin.add_view(AnalyticsView(name='Site Analytics', endpoint='analytics', category='General'))
admin.add_view(AboutAdmin(About, name="Manage About Me", category="About Me"))
admin.add_view(BaseModelView(Experience, name="Manage Experience", category="About Me"))
admin.add_view(BaseModelView(Skill, name="Manage Skills", category="About Me"))
admin.add_view(BaseModelView(Interest, name="Manage Interests", category="About Me"))
admin.add_view(BaseModelView(Tool, name="Manage Tools", category="About Me"))
admin.add_view(BaseModelView(Language, name="Manage Languages", category="About Me"))
admin.add_view(BaseModelView(Achievement, name="Manage Achievements", category="About Me"))
admin.add_view(BaseModelView(Certificate, name="Manage Certificates", category="About Me"))

admin.add_view(PageSettingsAdmin(ProjectsPage, name="Page Settings", category="Projects"))
admin.add_view(ProjectAdmin(Project, name="Manage Projects", category="Projects"))

admin.add_view(PageSettingsAdmin(BlogsPage, name="Page Settings", category="Blogs"))
admin.add_view(BlogAdmin(Blog, name="Manage Blogs", category="Blogs"))

admin.add_view(PageSettingsAdmin(DiaryPage, name="Page Settings", category="My Diary"))
admin.add_view(DiaryAdmin(Diary, name="Manage My Diary", category="My Diary"))

class ContactMessageAdmin(BaseModelView):
    column_searchable_list = ("name", "email", "subject", "message")
    column_filters = ("is_read", "subject")
    column_default_sort = ("created_at", True)
    can_create = False
    can_edit = True
    can_delete = True

admin.add_view(ContactMessageAdmin(ContactMessage, name="Messages & Inquiries", category="General"))
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
        "long_description": p.long_description or "",
        "hero_image": p.hero_image,
        "repo_url": p.repo_url,
        "live_url": p.live_url,
        "category": p.category,
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
        "likes": b.likes,
        "order": b.order
    }

def about_to_dict(a):
    return {
        "id": str(a.id),
        "title": a.title,
        "body": a.body,
        "hero_image": a.hero_image,
        "whatsapp": a.whatsapp,
        "email": a.email,
        "resume": a.resume,
        "skills": [skill_to_dict(s) for s in Skill.objects.order_by("order")],
        "interests": [interest_to_dict(i) for i in Interest.objects.order_by("order")],
        "tools": [tool_to_dict(t) for t in Tool.objects.order_by("order")],
        "languages": [language_to_dict(l) for l in Language.objects.order_by("order")],
        "achievements": [achievement_to_dict(xc) for xc in Achievement.objects.order_by("order")],
        "experiences": [experience_to_dict(e) for e in Experience.objects.order_by("order")],
    }


def is_placeholder_value(value):
    if value is None:
        return True
    cleaned = str(value).strip().lower()
    return not cleaned or cleaned.startswith("your-") or cleaned in {"changeme", "replace-me", "example"}


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
def logout():
    if current_user.is_authenticated:
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
        return jsonify({"title": "About Me", "body": "", "hero_image": "", "resume": ""})
    return jsonify(about_to_dict(about))

@app.route("/api/download-resume")
def api_download_resume():
    import re
    about = About.objects.first()
    if not about or not about.resume:
        abort(404, description="Resume not uploaded yet.")
    
    resume_url = about.resume.strip()
    
    # 1. Google Drive: convert view/sharing link to direct download link
    # Matches: /file/d/FILE_ID/view, /open?id=FILE_ID, /uc?id=FILE_ID
    gdrive_match = re.search(r'drive\.google\.com/(?:file/d/|open\?id=|uc\?id=)?([a-zA-Z0-9_-]{25,})', resume_url)
    if gdrive_match:
        file_id = gdrive_match.group(1)
        direct_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        return redirect(direct_url, code=302)
    
    # 2. Dropbox: convert dl=0 preview link to dl=1 direct download
    if 'dropbox.com' in resume_url:
        direct_url = re.sub(r'[?&]dl=0', '', resume_url)
        if '?' in direct_url:
            direct_url += '&dl=1'
        else:
            direct_url += '?dl=1'
        return redirect(direct_url, code=302)
    
    # 3. Direct PDF/DOCX or cloud URL (Cloudinary, AWS S3, local, etc.)
    return redirect(resume_url, code=302)

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

@app.route("/api/blogs/<slug>/like", methods=["POST"])
def api_blog_like(slug):
    data = request.get_json()
    session_id = data.get("session_id") if data else None
    
    if not session_id:
        return jsonify({"error": "Missing session_id"}), 400
        
    blog = Blog.objects(slug=slug).first()
    if not blog:
        abort(404)
        
    # Check if already liked in this session
    existing_like = LikeEvent.objects(blog_slug=slug, session_id=session_id).first()
    if existing_like:
        return jsonify({"message": "Already liked", "likes": blog.likes}), 200
        
    # Increment likes and record event
    blog.likes += 1
    blog.save()
    
    like_event = LikeEvent(blog_slug=slug, session_id=session_id, timestamp=datetime.now(timezone.utc))
    like_event.save()
    
    return jsonify({"message": "Liked successfully", "likes": blog.likes}), 201

@app.route("/api/analytics", methods=["POST"])
def api_analytics():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    session_id = data.get("session_id")
    path = data.get("path")
    scroll_depth = data.get("scroll_depth", 0)
    referrer = data.get("referrer") or "Direct / Bookmark"
    device_type = data.get("device_type") or "Desktop"
    browser = data.get("browser") or "Unknown"
    os = data.get("os") or "Unknown"
    screen_resolution = data.get("screen_resolution") or ""
    
    if not session_id or not path:
        return jsonify({"error": "Missing required fields (session_id or path)"}), 400

    # Get client IP and User Agent
    ip_address = request.headers.get("X-Forwarded-For", request.remote_addr)
    if ip_address and "," in ip_address:
        ip_address = ip_address.split(",")[0].strip()
    user_agent = request.headers.get("User-Agent")

    # Update or create session visit event
    today_start = datetime.now(pytz.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    existing_event = VisitEvent.objects(
        session_id=session_id, 
        path=path,
        timestamp__gte=today_start
    ).first()

    if existing_event:
        # Update scroll depth if it's higher
        if scroll_depth > existing_event.scroll_depth:
            existing_event.scroll_depth = scroll_depth
        existing_event.timestamp = datetime.now(pytz.utc)
        if referrer and existing_event.referrer == "Direct / Bookmark":
            existing_event.referrer = referrer
        existing_event.save()
        return jsonify({"status": "updated sequence"}), 200
    else:
        # Create new enriched event
        new_event = VisitEvent(
            session_id=session_id,
            path=path,
            ip_address=ip_address,
            user_agent=user_agent,
            referrer=referrer,
            device_type=device_type,
            browser=browser,
            os=os,
            screen_resolution=screen_resolution,
            timestamp=datetime.now(pytz.utc),
            scroll_depth=scroll_depth
        )
        new_event.save()
        return jsonify({"status": "created"}), 201

@app.route("/api/contact", methods=["POST"])
def api_contact():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    subject = (data.get("subject") or "General Inquiry").strip()
    message = (data.get("message") or "").strip()
    captcha_token = (data.get("captchaToken") or "").strip()

    if not name or not email or not message:
        return jsonify({"error": "Name, email, and message are required."}), 400

    # Basic email format check
    if "@" not in email or "." not in email:
        return jsonify({"error": "Please provide a valid email address."}), 400

    recaptcha_secret = (Config.RECAPTCHA_SECRET_KEY or "").strip()
    if recaptcha_secret and not is_placeholder_value(recaptcha_secret):
        if not captcha_token:
            return jsonify({"error": "Please complete the captcha verification before submitting."}), 400

        try:
            verify_response = requests.post(
                "https://www.google.com/recaptcha/api/siteverify",
                data={
                    "secret": recaptcha_secret,
                    "response": captcha_token,
                },
                timeout=10,
            )
            verify_response.raise_for_status()
            verification = verify_response.json()
            if not verification.get("success"):
                return jsonify({"error": "Captcha verification failed. Please try again."}), 400
        except Exception:
            return jsonify({"error": "Captcha verification could not be completed. Please try again."}), 400

    contact = ContactMessage(
        name=name,
        email=email,
        subject=subject,
        message=message,
        created_at=datetime.now(timezone.utc),
        is_read=False
    )
    contact.save()

    return jsonify({"status": "success", "message": "Your message has been sent successfully! I'll get back to you soon."}), 201

# --------------------------------------------------------------------
# SEO: Dynamic XML sitemap
# --------------------------------------------------------------------

@app.route("/api/sitemap.xml")
def api_sitemap():
    """Dynamically generate an XML sitemap that always reflects the
    current set of pages, blog posts, and diary entries."""
    domain = os.getenv("SITE_URL", "https://www.dipendrakumaryadav.com.np")

    # Static / main pages: (path, priority, changefreq)
    static_pages = [
        ("/", "1.0", "weekly"),
        ("/aboutme", "0.8", "monthly"),
        ("/blog", "0.9", "weekly"),
        ("/projects", "0.9", "weekly"),
        ("/mydiary", "0.8", "weekly"),
        ("/hire-me", "0.7", "monthly"),
    ]

    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    for path, priority, changefreq in static_pages:
        lines.append("  <url>")
        lines.append(f"    <loc>{escape(domain + path)}</loc>")
        lines.append(f"    <changefreq>{changefreq}</changefreq>")
        lines.append(f"    <priority>{priority}</priority>")
        lines.append("  </url>")

    # Blog posts -> /blog/<slug>
    for b in Blog.objects.all().order_by("-published_at"):
        lines.append("  <url>")
        lines.append(f"    <loc>{escape(domain + '/blog/' + b.slug)}</loc>")
        if b.published_at:
            lines.append(f"    <lastmod>{b.published_at.isoformat()}</lastmod>")
        lines.append("    <changefreq>monthly</changefreq>")
        lines.append("    <priority>0.8</priority>")
        lines.append("  </url>")

    # Diary entries -> /mydiary/<slug>
    for d in Diary.objects.all().order_by("-date"):
        lines.append("  <url>")
        lines.append(f"    <loc>{escape(domain + '/mydiary/' + d.slug)}</loc>")
        if d.date:
            lines.append(f"    <lastmod>{d.date.isoformat()}</lastmod>")
        lines.append("    <changefreq>monthly</changefreq>")
        lines.append("    <priority>0.7</priority>")
        lines.append("  </url>")

    lines.append("</urlset>")
    xml = "\n".join(lines)

    return Response(xml, mimetype="application/xml")

# --------------------------------------------------------------------
# Entrypoint
# --------------------------------------------------------------------

if __name__ == "__main__":
    # In production, Render will provide a PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    # Only enable debug mode in development
    debug_mode = os.getenv("FLASK_ENV") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
