#!/usr/bin/env python
"""Script to create a demo user for testing."""

from backend.app.database import SessionLocal, engine, Base
from backend.app.models.user import User
from backend.app.models.document import Document
from backend.app.models.conversation import Conversation
from backend.app.models.compliance import ComplianceReport
from backend.app.core.security import get_password_hash

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # Check if demo user already exists
    existing = db.query(User).filter(User.username == 'demo').first()
    if existing:
        print('❌ Utilisateur demo existe déjà')
    else:
        # Create demo user
        demo_user = User(
            username='demo',
            email='demo@textilebot.com',
            hashed_password=get_password_hash('demo123')
        )
        db.add(demo_user)
        db.commit()
        print('✅ Utilisateur demo créé avec succès')
        print('   Identifiant: demo')
        print('   Mot de passe: demo123')
finally:
    db.close()
