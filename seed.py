from models import db, Project, Diary, DiarySection, DiaryBullet, Blog, Certificate, About, HomeCard, User, Experience, Skill, Interest, Tool, Language, Achievement, ProjectsPage, BlogsPage, DiaryPage
from werkzeug.security import generate_password_hash
from datetime import date

def seed_data():
    print("Seeding data (updating existing records)...")

    # --- Page Metadata (Singletons) ---
    ProjectsPage.objects(title="Projects").update_one(
        upsert=True,
        set__hero_image="img/projects-hero.jpg",
        set__description="Here are some of the projects I've worked on."
    )
    BlogsPage.objects(title="Blogs").update_one(
        upsert=True,
        set__hero_image="img/blog-hero.jpg",
        set__description="Technical articles and guides."
    )
    DiaryPage.objects(title="Diary").update_one(
        upsert=True,
        set__hero_image="img/diary-hero.jpg",
        set__description="My personal diary and thoughts."
    )
    About.objects(title="About Me").update_one(
        upsert=True, 
        set__body="I am Dipendra Yadav, an automation and platform engineer passionate about building reliable, scalable, and sustainable systems...",
        set__hero_image="img/sunset.jpg",
        set__whatsapp="+917742228345",
        set__email="dipendrayadav299@gmail.com"
    )
    print("Seeded Page Metadata.")

    # --- Projects ---
    project_data = [
        {
            "slug": "wae",
            "title": "wae (Wasi App Experiment)",
            "short_description": "A project showcasing development in the Wasi world.",
            "long_description": "A project which showcases latest development in wasi world. Currently its updated for wasm v0.2. It helps in accumulating learnings from ML, Green Software and Wasi into a single repo.",
            "hero_image": "img/project-wae.jpg",
            "repo_url": "https://github.com/yourname/wae",
            "live_url": "#",
            "category": "Personal",
            "order": 1
        },
        {
            "slug": "raft-datastore",
            "title": "Raft based Distributed Consensus",
            "short_description": "Raft based Distributed Consensus enabled datastore",
            "long_description": "Implementation of Raft consensus algorithm for a distributed datastore.",
            "repo_url": "https://github.com/yourname/raft",
            "category": "Personal",
            "order": 2
        },
        {
            "slug": "cicd-manager",
            "title": "Universal CI/CD pipeline manager",
            "short_description": "Manage CI/CD pipelines universally.",
            "repo_url": "https://github.com/yourname/cicd",
            "category": "Real Client",
            "order": 3
        }
    ]
    for p in project_data:
        Project.objects(slug=p['slug']).update_one(upsert=True, **{f"set__{k}": v for k, v in p.items()})
    print("Seeded Projects.")

    # --- Diary ---
    diary_data = [
        {
            "slug": "nov-2025",
            "month_label": "[2025-11] Diary for November 2025",
            "date": date(2025, 11, 1),
            "summary": "Let's talk about my November 2025",
            "word_count": 309,
            "sections": [
                DiarySection(
                    title="Date 2025-11-25 to 2025-11-30",
                    order=1,
                    bullets=[
                        DiaryBullet(text="some health issues", order=1),
                        DiaryBullet(text="The project's billing system is being upgraded from Stripe to Polar.sh.", order=2),
                        DiaryBullet(text="New connections and settings were added for the new billing system.", order=3),
                        DiaryBullet(text="More experience with event based architecture.", order=4),
                    ]
                )
            ]
        },
        {
            "slug": "oct-2025",
            "month_label": "[2025-10] Diary for October 2025",
            "date": date(2025, 10, 1),
            "summary": "Let's talk about my October 2025",
            "word_count": 0
        }
    ]
    for d in diary_data:
        Diary.objects(slug=d['slug']).update_one(upsert=True, **{f"set__{k}": v for k, v in d.items()})
    print("Seeded Diaries.")

    # --- Blogs ---
    blog_data = [
        {
            "slug": "opentelemetry-guide",
            "title": "My First Two Months with OpenTelemetry",
            "subtitle": "A Practical Guide",
            "published_at": date(2025, 1, 15),
            "read_time_min": 5,
            "hero_image": "img/blog-opentelemetry.jpg",
            "content": "A developer-friendly walkthrough for instrumenting services with OpenTelemetry...",
            "order": 1
        },
        {
            "slug": "docker-firewall",
            "title": "When Docker's Firewall Blocks Your Virt-Manager VM",
            "subtitle": "Troubleshooting guide",
            "published_at": date(2025, 1, 10),
            "read_time_min": 3,
            "hero_image": "img/blog-docker-firewall.jpg",
            "content": "Troubleshooting guide for fixing network connectivity between Docker and virt-manager VMs...",
            "order": 2
        }
    ]
    for b in blog_data:
        Blog.objects(slug=b['slug']).update_one(upsert=True, **{f"set__{k}": v for k, v in b.items()})
    print("Seeded Blogs.")

    # --- Home Cards ---
    card_data = [
        {
            "title": "Let’s talk about me",
            "image_url": "https://picsum.photos/id/1015/800/600",
            "alt_text": "ocean sunset",
            "link_url": "/aboutme",
            "order": 1
        },
        {
            "title": "Tech blogs",
            "image_url": "https://picsum.photos/id/1060/800/600",
            "alt_text": "notebook & glasses",
            "link_url": "/blog",
            "order": 2
        },
        {
            "title": "Projects and OSS",
            "image_url": "https://picsum.photos/id/1025/800/600",
            "alt_text": "post-it & pens",
            "link_url": "/projects",
            "order": 3
        }
    ]
    for c in card_data:
        HomeCard.objects(title=c['title']).update_one(upsert=True, **{f"set__{k}": v for k, v in c.items()})
    print("Seeded Home Cards.")

    # --- Admin User ---
    if not User.objects(username="admin").first():
        admin_user = User(
            username="admin",
            password_hash=generate_password_hash("admin123")
        )
        admin_user.save()
        print("Seeded Admin User (admin / admin123).")


    # --- About (Individual Sections) ---
    print("Seeding About Me individual sections...")
    
    # Experiences
    exp_data = [
        {
            "company_name": "rtCamp",
            "company_logo": "img/rtcamp_logo.png",
            "role": "DevOps Engineer",
            "tenure": "01/2024 to Present",
            "contributions": [
                "Implemented self-hosted multi-runner architecture, improving CI/CD developer velocity by 50% and optimizing infrastructure utilization by 40%.",
                "Migrated to self-hosted Google Tag Manager, reducing network calls to third-party consumers and improving page performance.",
                "Designed Kubernetes-based WordPress deployments with 10x higher availability and fault tolerance.",
                "Built a deployment dashboard with Terraform-powered BYOC support, reducing site go-live time by 2x.",
                "Developed internal automation tools with Frappe and Ansible (multi-runner provisioning, certbot integration, monitoring with New Relic).",
                "Implemented optimizations for AWS Savings Plans (EC2 + RDS) and integrated Cloudflare + Fail2Ban for enhanced security."
            ],
            "order": 1
        },
        {
            "company_name": "Viamagus",
            "role": "Junior DevOps Engineer",
            "tenure": "2023",
            "contributions": ["Assisted in cloud infrastructure management.", "Automated CI/CD pipelines."],
            "order": 2
        },
        {
            "company_name": "Ksctl",
            "role": "Creator & Lead Developer",
            "tenure": "2023 - Present",
            "contributions": ["Built a carbon-aware Kubernetes CLI.", "Optimized multi-cloud cluster management."],
            "order": 3
        },
        {
            "company_name": "Kubesimplify",
            "role": "Cloud Native Contributor",
            "tenure": "2023",
            "contributions": ["Contributed to open-source cloud native tutorials.", "Engaged with the community for CNCF projects."],
            "order": 4
        },
        {
            "company_name": "Viamagus (Previous)",
            "role": "Intern",
            "tenure": "2022",
            "contributions": ["Introduction to web development and cloud concepts."],
            "order": 5
        }
    ]
    for e in exp_data:
        Experience.objects(company_name=e['company_name']).update_one(upsert=True, **{f"set__{k}": v for k, v in e.items()})
    print("Seeded Experiences.")

    # Skills
    skill_data = [
        {"name": "DevOps", "category": "Platform", "level": "Advanced", "order": 1},
        {"name": "Kubernetes", "category": "Infrastructure", "level": "Advanced", "order": 2},
        {"name": "Cloud Native", "category": "General", "level": "Advanced", "order": 3},
        {"name": "CI/CD", "category": "Process", "level": "Expert", "order": 4}
    ]
    for s in skill_data:
        Skill.objects(name=s['name']).update_one(upsert=True, **{f"set__{k}": v for k, v in s.items()})
    print("Seeded Skills.")

    # Interests
    interest_data = [
        {"name": "Green Software", "order": 1},
        {"name": "Cloud Native Computing", "order": 2},
        {"name": "Automation", "order": 3}
    ]
    for i in interest_data:
        Interest.objects(name=i['name']).update_one(upsert=True, **{f"set__{k}": v for k, v in i.items()})
    print("Seeded Interests.")

    # Tools
    tool_data = [
        {"name": "Terraform", "order": 1},
        {"name": "Docker", "order": 2},
        {"name": "Ansible", "order": 3},
        {"name": "GitHub Actions", "order": 4}
    ]
    for t in tool_data:
        Tool.objects(name=t['name']).update_one(upsert=True, **{f"set__{k}": v for k, v in t.items()})
    print("Seeded Tools.")

    # Languages
    lang_data = [
        {"name": "Python", "level": "Expert", "order": 1},
        {"name": "Go", "level": "Advanced", "order": 2},
        {"name": "JavaScript", "level": "Intermediate", "order": 3}
    ]
    for l in lang_data:
        Language.objects(name=l['name']).update_one(upsert=True, **{f"set__{k}": v for k, v in l.items()})
    print("Seeded Languages.")

    # Achievements
    ach_data = [
        {"title": "Winner — Nappitive + WeMakeDevs Cloud Native Hackathon", "description": "Recognized for building innovative cloud solutions.", "order": 1},
        {"title": "Built Ksctl", "description": "Carbon-aware Kubernetes CLI.", "order": 2},
        {"title": "Developed DevSecOps Pipelines", "description": "Integrated security and MLOps into CI/CD.", "order": 3}
    ]
    for a in ach_data:
        Achievement.objects(title=a['title']).update_one(upsert=True, **{f"set__{k}": v for k, v in a.items()})
    print("Seeded Achievements.")
    
    # Certificates
    cert_data = [
        {"name": "AWS Certified Cloud Practitioner", "image_url": "img/aws-cert.jpg", "link_url": "https://aws.amazon.com/", "order": 1},
        {"name": "CKAD: Certified Kubernetes Application Developer", "image_url": "img/ckad-cert.jpg", "link_url": "https://training.linuxfoundation.org/", "order": 2}
    ]
    for c in cert_data:
        Certificate.objects(name=c['name']).update_one(upsert=True, **{f"set__{k}": v for k, v in c.items()})
    print("Seeded Certificates.")
    
    print("Database seeding/update complete!")

if __name__ == "__main__":
    from app import app
    with app.app_context():
        seed_data()
