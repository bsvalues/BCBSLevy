"""
Web Scraper Application - Database models.

This module defines the database models for the web scraping application.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy
db = SQLAlchemy()

class ScrapeRequest(db.Model):
    """Model for storing scrape requests."""
    __tablename__ = 'scrape_requests'
    
    id = Column(Integer, primary_key=True)
    url = Column(String(500), nullable=False, index=True)
    status = Column(String(20), nullable=False, default='pending', index=True)  # pending, processing, completed, failed
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Relationship with scraped content
    scraped_content = relationship("ScrapedContent", back_populates="scrape_request", uselist=False, cascade="all, delete-orphan")

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'url': self.url,
            'status': self.status,
            'created_at': self.created_at,
            'completed_at': self.completed_at,
            'error_message': self.error_message
        }


class ScrapedContent(db.Model):
    """Model for storing scraped content."""
    __tablename__ = 'scraped_contents'
    
    id = Column(Integer, primary_key=True)
    scrape_request_id = Column(Integer, ForeignKey('scrape_requests.id', ondelete='CASCADE'), nullable=False, unique=True)
    content = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationship with scrape request
    scrape_request = relationship("ScrapeRequest", back_populates="scraped_content")

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'scrape_request_id': self.scrape_request_id,
            'content': self.content,
            'created_at': self.created_at
        }