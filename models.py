from flask_mongoengine import MongoEngine
from flask_login import UserMixin
from datetime import date

db = MongoEngine()

class Project(db.DynamicDocument):
    slug = db.StringField(unique=True, required=True)
    title = db.StringField(required=True)
    short_description = db.StringField(required=True)
    long_description = db.StringField()
    hero_image = db.StringField()
    repo_url = db.StringField()
    live_url = db.StringField()
    order = db.IntField(default=0)

    def __repr__(self):
        return f"<Project {self.slug}>"

class ProjectsPage(db.DynamicDocument):
    title = db.StringField(default="Projects")
    hero_image = db.StringField()
    description = db.StringField()
    # projects = db.ListField(db.EmbeddedDocumentField(Project)) # Removed

    def __repr__(self):
        return f"<ProjectsPage {self.title}>"

class DiaryBullet(db.EmbeddedDocument):
    text = db.StringField(required=True)
    order = db.IntField(default=0)

class DiarySection(db.EmbeddedDocument):
    title = db.StringField(required=True)
    order = db.IntField(default=0)
    bullets = db.ListField(db.EmbeddedDocumentField(DiaryBullet))

class Diary(db.DynamicDocument):
    slug = db.StringField(unique=True, required=True)
    month_label = db.StringField(required=True)
    date = db.DateField(required=True, default=date.today)
    author = db.StringField(default="Dipendra Yadav")
    summary = db.StringField(required=True)
    word_count = db.IntField(default=0)
    sections = db.ListField(db.EmbeddedDocumentField(DiarySection))

    def __repr__(self):
        return f"<Diary {self.slug}>"

class DiaryPage(db.DynamicDocument):
    title = db.StringField(default="Diary")
    hero_image = db.StringField()
    description = db.StringField()
    # diaries = db.ListField(db.EmbeddedDocumentField(Diary)) # Removed

    def __repr__(self):
        return f"<DiaryPage {self.title}>"

class Certificate(db.DynamicDocument):
    name = db.StringField(required=True)
    image_url = db.StringField()
    link_url = db.StringField()
    order = db.IntField(default=0)

    def __repr__(self):
        return f"<Certificate {self.name}>"

class Skill(db.DynamicDocument):
    name = db.StringField(required=True)
    category = db.StringField()  # e.g., "Frontend", "Backend"
    level = db.StringField()     # e.g., "Intermediate", "Advanced"
    order = db.IntField(default=0)

    def __repr__(self):
        return f"<Skill {self.name}>"

class Interest(db.DynamicDocument):
    name = db.StringField(required=True)
    order = db.IntField(default=0)

    def __repr__(self):
        return f"<Interest {self.name}>"

class Tool(db.DynamicDocument):
    name = db.StringField(required=True)
    icon_url = db.StringField()
    order = db.IntField(default=0)

    def __repr__(self):
        return f"<Tool {self.name}>"

class Language(db.DynamicDocument):
    name = db.StringField(required=True)
    level = db.StringField()
    order = db.IntField(default=0)

    def __repr__(self):
        return f"<Language {self.name}>"

class Achievement(db.DynamicDocument):
    title = db.StringField(required=True)
    description = db.StringField()
    date = db.DateField()
    order = db.IntField(default=0)

    def __repr__(self):
        return f"<Achievement {self.title}>"

class Experience(db.DynamicDocument):
    company_name = db.StringField(required=True)
    company_logo = db.StringField()
    role = db.StringField(required=True)
    tenure = db.StringField(required=True)
    contributions = db.ListField(db.StringField())
    order = db.IntField(default=0)

    def __repr__(self):
        return f"<Experience {self.company_name}>"

class About(db.DynamicDocument):
    title = db.StringField(default="About Me")
    body = db.StringField()
    hero_image = db.StringField()
    
    # Embedded Sections Removed
    # skills = db.ListField(db.EmbeddedDocumentField(Skill))
    # interests = db.ListField(db.EmbeddedDocumentField(Interest))
    # tools = db.ListField(db.EmbeddedDocumentField(Tool))
    # languages = db.ListField(db.EmbeddedDocumentField(Language))
    # achievements = db.ListField(db.EmbeddedDocumentField(Achievement))
    # experiences = db.ListField(db.EmbeddedDocumentField(Experience))

    def __repr__(self):
        return f"<About {self.title}>"

class Blog(db.DynamicDocument):
    slug = db.StringField(unique=True, required=True)
    title = db.StringField(required=True)
    subtitle = db.StringField()
    published_at = db.DateField(required=True, default=date.today)
    author = db.StringField(default="Dipendra Yadav")
    read_time_min = db.IntField(default=2)
    word_count = db.IntField(default=0)
    hero_image = db.StringField()
    content = db.StringField()
    order = db.IntField(default=0)

    def __repr__(self):
        return f"<Blog {self.slug}>"

class BlogsPage(db.DynamicDocument):
    title = db.StringField(default="Blogs")
    hero_image = db.StringField()
    description = db.StringField()
    # blogs = db.ListField(db.EmbeddedDocumentField(Blog)) # Removed

    def __repr__(self):
        return f"<BlogsPage {self.title}>"

class HomeCard(db.DynamicDocument):
    title = db.StringField(required=True)
    image_url = db.StringField(required=True)
    alt_text = db.StringField()
    link_url = db.StringField(required=True)
    order = db.IntField(default=0)

    def __repr__(self):
        return f"<HomeCard {self.title}>"

class User(db.Document, UserMixin):
    username = db.StringField(unique=True, required=True)
    password_hash = db.StringField(required=True)

    def __repr__(self):
        return f"<User {self.username}>"
