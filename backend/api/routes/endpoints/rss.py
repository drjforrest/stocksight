from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from xml.etree.ElementTree import Element, SubElement, tostring
import hashlib
import secrets

from backend.config.database import get_db
from backend.models.tracked_company import TrackedCompany
from backend.models.news import NewsArticle, NewsCompanyMention
from backend.services.cache import CacheService

router = APIRouter(
    prefix="/rss",
    tags=["rss"]
)

# Initialize cache service
cache = CacheService()

@router.get("/token/{user_id}")
async def generate_feed_token(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Generate or retrieve a unique RSS feed token for a user.
    This token can be used to access their personalized RSS feed.
    
    Args:
        user_id: ID of the user
        db: Database session
    """
    # Check if token exists in cache
    token_key = f"rss_token:{user_id}"
    token = await cache.get(token_key)
    
    if not token:
        # Generate new token if not exists
        token = secrets.token_urlsafe(32)
        await cache.set(token_key, token)
        
        # Also store reverse mapping for validation
        await cache.set(f"rss_user:{token}", str(user_id))
    
    feed_url = f"/rss/feed/{token}"
    return {
        "token": token,
        "feed_url": feed_url
    }

@router.get("/feed/{token}")
async def get_rss_feed(
    token: str,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """
    Get RSS feed using a user's feed token.
    
    Args:
        token: User's RSS feed token
        days: Number of days of news to include (default: 7)
        db: Database session
    """
    # Validate token and get user_id
    user_id = await cache.get(f"rss_user:{token}")
    if not user_id:
        raise HTTPException(
            status_code=404,
            detail="Invalid RSS feed token"
        )
    
    # Check cache for recent feed
    cache_key = f"rss_feed:{token}:{days}"
    cached_feed = await cache.get(cache_key)
    if cached_feed:
        return Response(
            content=cached_feed,
            media_type="application/xml",
            headers={"Content-Disposition": "attachment; filename=stocksight_news.xml"}
        )
    
    # Get tracked companies
    tracked_companies = db.query(TrackedCompany.company_symbol).filter(
        TrackedCompany.user_id == int(user_id)
    ).all()
    
    if not tracked_companies:
        raise HTTPException(
            status_code=404,
            detail="No tracked companies found"
        )
    
    symbols = [company[0] for company in tracked_companies]
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Get news articles for tracked companies
    articles = db.query(NewsArticle)\
        .join(NewsArticle.mentions)\
        .filter(
            NewsCompanyMention.company_symbol.in_(symbols),
            NewsArticle.published_at >= cutoff_date
        )\
        .order_by(NewsArticle.published_at.desc())\
        .all()
    
    # Generate RSS XML
    rss = Element("rss", version="2.0")
    channel = SubElement(rss, "channel")
    
    # Add channel metadata
    SubElement(channel, "title").text = "StockSight News Feed"
    SubElement(channel, "description").text = f"Latest news for tracked companies: {', '.join(symbols)}"
    SubElement(channel, "link").text = "https://stocksight.app"
    SubElement(channel, "language").text = "en-us"
    SubElement(channel, "pubDate").text = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
    
    # Add feed ID for caching
    feed_id = hashlib.md5(f"{token}:{days}:{datetime.utcnow().strftime('%Y-%m-%d')}".encode()).hexdigest()
    SubElement(channel, "feedId").text = feed_id
    
    # Add news items
    for article in articles:
        item = SubElement(channel, "item")
        SubElement(item, "title").text = article.title
        SubElement(item, "link").text = article.url
        
        # Add content if available
        if article.content:
            SubElement(item, "description").text = article.content
            
        # Add sentiment if available
        if article.sentiment_score is not None:
            sentiment_elem = SubElement(item, "sentiment")
            sentiment_elem.text = str(article.sentiment_score)
        
        # Add publication date
        pub_date = article.published_at.strftime("%a, %d %b %Y %H:%M:%S GMT")
        SubElement(item, "pubDate").text = pub_date
        
        # Add source and company symbols
        SubElement(item, "source").text = article.source
        mentions = [mention.company_symbol for mention in article.mentions]
        SubElement(item, "companies").text = ", ".join(mentions)
    
    # Convert to XML string
    rss_feed = tostring(rss, encoding="utf-8", method="xml")
    
    # Cache the feed for 1 hour
    await cache.set(cache_key, rss_feed, expire=3600)
    
    return Response(
        content=rss_feed,
        media_type="application/xml",
        headers={"Content-Disposition": "attachment; filename=stocksight_news.xml"}
    )

@router.get("/preferences/{user_id}")
async def get_feed_preferences(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get user's RSS feed preferences.
    
    Args:
        user_id: ID of the user
        db: Database session
    """
    # TODO: Implement feed preferences (frequency, content filters, etc.)
    return {
        "default_days": 7,
        "include_sentiment": True,
        "content_type": "full",  # or "summary"
        "update_frequency": "hourly"
    } 