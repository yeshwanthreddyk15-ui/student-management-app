import sys
sys.path.insert(0, r'c:\Users\yeshw\Desktop\VS code\app')
from app import app, User
import json

with app.app_context():
    users = [(u.id, u.username, u.role) for u in User.query.all()]
    print(json.dumps(users))
