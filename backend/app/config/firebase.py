"""
SmartArena AI — Firebase Initialization
========================================

Initializes Firebase Admin SDK and provides a singleton Firestore client.
Uses Application Default Credentials in production (Cloud Run)
and service account JSON in development.
"""

import os
import logging
from typing import Optional

import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask
from google.cloud.firestore_v1.client import Client as FirestoreClient

logger = logging.getLogger(__name__)

# Module-level singleton
_firestore_client: Optional[FirestoreClient] = None


def init_firebase(app: Flask) -> None:
    """Initialize Firebase Admin SDK.

    Attempts to use service account credentials file first,
    then falls back to Application Default Credentials (ADC).

    Args:
        app: Flask application instance.
    """
    global _firestore_client

    if firebase_admin._apps:
        logger.info("Firebase already initialized, skipping")
        _firestore_client = firestore.client()
        return

    project_id: str = app.config.get("FIREBASE_PROJECT_ID", "")
    cred_path: str = app.config.get("FIREBASE_CREDENTIALS_PATH", "")

    try:
        if cred_path and os.path.exists(cred_path):
            # Development: Use service account JSON
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred, {"projectId": project_id})
            logger.info("Firebase initialized with service account credentials")
        elif project_id:
            # Production: Use Application Default Credentials
            firebase_admin.initialize_app(options={"projectId": project_id})
            logger.info("Firebase initialized with ADC for project: %s", project_id)
        else:
            logger.warning(
                "Firebase not configured — set FIREBASE_PROJECT_ID "
                "and/or FIREBASE_CREDENTIALS_PATH"
            )
            return

        _firestore_client = firestore.client()
        logger.info("Firestore client ready")

    except Exception as e:
        logger.error("Firebase initialization failed: %s", str(e))
        logger.warning("App will run without Firebase — some features disabled")


def get_firestore_client() -> Optional[FirestoreClient]:
    """Get the singleton Firestore client.

    Returns:
        Firestore client instance, or None if Firebase is not initialized.
    """
    return _firestore_client
