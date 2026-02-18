from app import app, admin

def diag_admin_views():
    with app.app_context():
        print(f"Admin Views Count: {len(admin._views)}")
        for view in admin._views:
            print(f"View: {view.name}, Endpoint: {view.endpoint}, Category: {view.category}")
        
        print("\n--- Menu Construction (Manual) ---")
        for item in admin.menu():
            print(f"Menu Item: {item.name}, Type: {type(item).__name__}")
            if hasattr(item, 'get_children'):
                children = item.get_children()
                print(f"  Children count: {len(children)}")
                for child in children:
                    print(f"    Child: {child.name}, URL: {child.get_url()}")

if __name__ == "__main__":
    diag_admin_views()
