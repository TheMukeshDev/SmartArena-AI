import os
import sys
import datetime
import logging

# Setup path so we can import from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from firebase_admin import auth, credentials, initialize_app
from app.config.firebase import get_firestore_client
from app import create_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app to load env and firebase setup
app = create_app()

def create_or_update_user(email, password, name, role):
    try:
        try:
            user = auth.get_user_by_email(email)
            logger.info(f"User {email} already exists. Updating...")
            auth.update_user(user.uid, password=password, display_name=name)
            uid = user.uid
        except auth.UserNotFoundError:
            logger.info(f"Creating user {email}...")
            user = auth.create_user(email=email, password=password, display_name=name)
            uid = user.uid

        # Set custom claims
        auth.set_custom_user_claims(uid, {'role': role})
        logger.info(f"Set role '{role}' in custom claims for {email}")

        # Update Firestore
        db = get_firestore_client()
        if db:
            db.collection("users").document(uid).set({
                "email": email,
                "name": name,
                "role": role,
                "createdAt": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }, merge=True)
            logger.info(f"Set role '{role}' in Firestore for {email}")
        
    except Exception as e:
        logger.error(f"Error processing user {email}: {str(e)}")

with app.app_context():
    create_or_update_user("admin@smartarena.ai", "Admin123!", "Test Admin", "admin")
    create_or_update_user("volunteer@smartarena.ai", "Volunteer123!", "Test Volunteer", "volunteer")
    create_or_update_user("fan@smartarena.ai", "Fan123!", "Test Fan", "fan")

logger.info("Done creating test users.")
