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

    if app.config.get("TESTING", False):
        logger.info("Testing mode — skipping Firebase initialization")
        return

    if firebase_admin._apps:
        logger.info("Firebase already initialized, skipping")
        _firestore_client = firestore.client()
        return

    project_id: str = app.config.get("FIREBASE_PROJECT_ID", "")
    client_email: str = app.config.get("FIREBASE_CLIENT_EMAIL", "")
    private_key: str = app.config.get("FIREBASE_PRIVATE_KEY", "")

    try:
        if client_email and private_key:
            # Development: Use service account dict from env vars
            cred_dict = {
                "type": "service_account",
                "project_id": project_id,
                "private_key": private_key.replace("\\n", "\n"),
                "client_email": client_email,
                "token_uri": "https://oauth2.googleapis.com/token",
            }
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred, {"projectId": project_id})
            logger.info("Firebase initialized with service account env credentials")
        elif project_id:
            # Production: Use Application Default Credentials
            firebase_admin.initialize_app(options={"projectId": project_id})
            logger.info("Firebase initialized with ADC for project: %s", project_id)
        else:
            logger.warning(
                "Firebase not configured — set FIREBASE_PROJECT_ID "
                "and FIREBASE_CLIENT_EMAIL/PRIVATE_KEY"
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
