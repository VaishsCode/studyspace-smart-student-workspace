from app import app, db, User

with app.app_context():
    # Change 'Vaishnavi Gadade' to your exact username if different
    admin_user = User.query.filter_by(username='Vaishnavi Gadade').first()
    
    if admin_user:
        admin_user.is_admin = True
        db.session.commit()
        print("Success! You are now an Admin.")
    else:
        print("Error: User not found. Check the spelling of the username.")