from app import app, admin
from flask_admin.menu import MenuCategory, MenuView, MenuLink

def diag_admin():
    with app.app_context():
        with app.test_request_context():
            print(f"Admin URL: {admin.url}")
            
            print("\n--- Menu Structure ---")
            for item in admin.menu():
                # Check for is_category method/property
                is_cat_val = "N/A"
                if hasattr(item, 'is_category'):
                    try:
                        is_cat_val = item.is_category()
                    except TypeError:
                        is_cat_val = item.is_category
                    except Exception as e:
                        is_cat_val = f"ERR: {e}"
                
                # Check for children
                children = getattr(item, 'children', "N/A")
                if children == "N/A":
                   children = getattr(item, 'get_children', lambda: [])()
                
                try:
                    url = item.get_url()
                except Exception as e:
                    url = f"ERROR: {e}"
                
                print(f"Item: {item.name}")
                print(f"  Type: {type(item).__name__}")
                print(f"  URL: {url}")
                print(f"  is_category(): {is_cat_val}")
                print(f"  Children count: {len(children) if not isinstance(children, str) else children}")
                
                if not isinstance(children, str):
                    for child in children:
                        try:
                            child_url = child.get_url()
                        except Exception as e:
                            child_url = f"ERROR: {e}"
                        print(f"    Child: {child.name}, URL: {child_url}")

if __name__ == "__main__":
    diag_admin()
