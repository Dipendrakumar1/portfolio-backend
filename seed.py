from app import app
from models import db, Project, Diary, DiarySection, DiaryBullet, Blog, Certificate, About, HomeCard, User, Experience
from werkzeug.security import generate_password_hash
from datetime import date

def seed_data():
    # Clear existing data
    Project.objects.delete()
    Diary.objects.delete()
    Blog.objects.delete()
    Certificate.objects.delete()
    About.objects.delete()
    HomeCard.objects.delete()
    User.objects.delete()
    Experience.objects.delete()

    print("Cleared existing data.")

    # --- Projects ---
    p1 = Project(
        slug="wae",
        title="wae (Wasi App Experiment)",
        short_description="A project showcasing development in the Wasi world.",
        long_description="A project which showcases latest development in wasi world. Currently its updated for wasm v0.2. It helps in accumulating learnings from ML, Green Software and Wasi into a single repo.",
        hero_image="img/project-wae.jpg",
        repo_url="https://github.com/yourname/wae",
        live_url="#"
    ).save()
    
    p2 = Project(
        slug="raft-datastore",
        title="Raft based Distributed Consensus",
        short_description="Raft based Distributed Consensus enabled datastore",
        long_description="Implementation of Raft consensus algorithm for a distributed datastore.",
        repo_url="https://github.com/yourname/raft"
    ).save()

    p3 = Project(
        slug="cicd-manager",
        title="Universal CI/CD pipeline manager",
        short_description="Manage CI/CD pipelines universally.",
        repo_url="https://github.com/yourname/cicd"
    ).save()

    print("Seeded Projects.")

    # --- Diary ---
    d1 = Diary(
        slug="nov-2025",
        month_label="[2025-11] Diary for November 2025",
        date=date(2025, 11, 1),
        summary="Let's talk about my November 2025",
        word_count=309,
        sections=[
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
    ).save()

    d2 = Diary(
        slug="oct-2025",
        month_label="[2025-10] Diary for October 2025",
        date=date(2025, 10, 1),
        summary="Let's talk about my October 2025",
        word_count=0
    ).save()

    print("Seeded Diaries.")

    # --- Blogs ---
    b1 = Blog(
        slug="opentelemetry-guide",
        title="My First Two Months with OpenTelemetry",
        subtitle="A Practical Guide",
        published_at=date(2025, 1, 15),
        read_time_min=5,
        hero_image="img/blog-opentelemetry.jpg",
        content="A developer-friendly walkthrough for instrumenting services with OpenTelemetry..."
    ).save()

    b2 = Blog(
        slug="docker-firewall",
        title="When Docker's Firewall Blocks Your Virt-Manager VM",
        subtitle="Troubleshooting guide",
        published_at=date(2025, 1, 10),
        read_time_min=3,
        hero_image="img/blog-docker-firewall.jpg",
        content="Troubleshooting guide for fixing network connectivity between Docker and virt-manager VMs..."
    ).save()

    print("Seeded Blogs.")

    # --- About ---
    About(
        title="About Me",
        body="I am Dipendra Yadav, an automation and platform engineer passionate about building reliable, scalable, and sustainable systems...",
        hero_image="img/sunset.jpg"
    ).save()

    print("Seeded About.")

    # --- Home Cards ---
    HomeCard(
        title="Let’s talk about me",
        image_url="https://picsum.photos/id/1015/800/600",
        alt_text="ocean sunset",
        link_url="/aboutme",
        order=1
    ).save()

    HomeCard(
        title="Tech blogs",
        image_url="https://picsum.photos/id/1060/800/600",
        alt_text="notebook & glasses",
        link_url="/blog",
        order=2
    ).save()

    HomeCard(
        title="Projects and OSS",
        image_url="https://picsum.photos/id/1025/800/600",
        alt_text="post-it & pens",
        link_url="/projects",
        order=3
    ).save()

    print("Seeded Home Cards.")

    # --- Admin User ---
    admin_user = User(
        username="admin",
        password_hash=generate_password_hash("admin123")
    )
    admin_user.save()
    print("Seeded Admin User (admin / admin123).")

    # --- Experiences ---
    rtcamp = Experience(
        company_name="rtCamp",
        company_logo="img/rtcamp_logo.png",
        role="DevOps Engineer",
        tenure="01/2024 to Present",
        contributions=[
            "Implemented self-hosted multi-runner architecture, improving CI/CD developer velocity by 50% and optimizing infrastructure utilization by 40%.",
            "Migrated to self-hosted Google Tag Manager, reducing network calls to third-party consumers and improving page performance.",
            "Designed Kubernetes-based WordPress deployments with 10x higher availability and fault tolerance.",
            "Built a deployment dashboard with Terraform-powered BYOC support, reducing site go-live time by 2x.",
            "Developed internal automation tools with Frappe and Ansible (multi-runner provisioning, certbot integration, monitoring with New Relic).",
            "Implemented optimizations for AWS Savings Plans (EC2 + RDS) and integrated Cloudflare + Fail2Ban for enhanced security."
        ],
        order=1
    )
    rtcamp.save()
    print("Seeded Experiences.")

    print("Database seeded successfully!")

if __name__ == "__main__":
    with app.app_context():
        seed_data()
