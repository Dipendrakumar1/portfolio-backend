from app import app, about_to_dict
from models import About, Skill, Interest, Tool, Language, Achievement, Experience

def debug_about():
    with app.app_context():
        try:
            print("Fetching About object...")
            about = About.objects.first()
            if not about:
                print("No About object found.")
                return
            
            print("Converting About to dict...")
            data = about_to_dict(about)
            print("Success!")
            # print(data)
        except Exception as e:
            print(f"Error caught: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_about()
