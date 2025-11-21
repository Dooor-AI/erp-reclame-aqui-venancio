"""
Test script to check if routes are loaded in the FastAPI app
"""
from app.main import app

print("=== Testing FastAPI App Routes ===\n")

# Get all routes from the app
for route in app.routes:
    if hasattr(route, 'path') and hasattr(route, 'methods'):
        print(f"{route.path} - {route.methods}")

print("\n=== Looking for timeline and location routes ===")
timeline_found = any('/timeline' in str(route.path) for route in app.routes if hasattr(route, 'path'))
location_found = any('/location' in str(route.path) for route in app.routes if hasattr(route, 'path'))

print(f"Timeline route found: {timeline_found}")
print(f"Location route found: {location_found}")
