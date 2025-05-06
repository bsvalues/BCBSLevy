"""
Web Scraper Application - Database models.

This module defines the database models used in the application.
"""

from datetime import datetime
from sqlalchemy import JSON, Text, ForeignKey, String, Integer, DateTime, Boolean
from sqlalchemy.orm import relationship
from app import db


class User(db.Model):
    """User model for authentication."""
    id = db.Column(Integer, primary_key=True)
    username = db.Column(String(64), unique=True, nullable=False)
    email = db.Column(String(120), unique=True, nullable=False)
    password_hash = db.Column(String(256))
    created_at = db.Column(DateTime, default=datetime.utcnow)
    
    scrape_requests = relationship('ScrapeRequest', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'


class ScrapeRequest(db.Model):
    """Model to store web scraping requests."""
    id = db.Column(Integer, primary_key=True)
    url = db.Column(String(500), nullable=False)
    status = db.Column(String(20), default='pending')  # pending, completed, failed
    created_at = db.Column(DateTime, default=datetime.utcnow)
    completed_at = db.Column(DateTime, nullable=True)
    user_id = db.Column(Integer, ForeignKey('user.id'), nullable=True)
    content_type = db.Column(String(50), default='text')  # text, table, structured
    error_message = db.Column(Text, nullable=True)
    
    scraped_content = relationship('ScrapedContent', backref='scrape_request', lazy=True, uselist=False)
    
    def __repr__(self):
        return f'<ScrapeRequest {self.id} {self.url}>'


class ScrapedContent(db.Model):
    """Model to store the scraped content."""
    id = db.Column(Integer, primary_key=True)
    scrape_request_id = db.Column(Integer, ForeignKey('scrape_request.id'), nullable=False)
    content = db.Column(Text, nullable=True)
    metadata = db.Column(JSON, nullable=True)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ScrapedContent for request {self.scrape_request_id}>'