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

    def __repr__(self):
        return f"<Project {self.slug}>"

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

class Certificate(db.DynamicDocument):
    name = db.StringField(required=True)
    image_url = db.StringField()
    link_url = db.StringField()

    def __repr__(self):
        return f"<Certificate {self.name}>"

class About(db.DynamicDocument):
    title = db.StringField(default="About Me")
    body = db.StringField()
    hero_image = db.StringField()

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

    def __repr__(self):
        return f"<Blog {self.slug}>"

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

class Experience(db.DynamicDocument):
    company_name = db.StringField(required=True)
    company_logo = db.StringField()
    role = db.StringField(required=True)
    tenure = db.StringField(required=True)
    contributions = db.ListField(db.StringField())
    order = db.IntField(default=0)

    def __repr__(self):
        return f"<Experience {self.company_name}>"
