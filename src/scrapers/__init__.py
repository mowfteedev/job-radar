"""Scrapers module exports."""
from src.scrapers.base import BaseScraper
from src.scrapers.fpt_telecom import FPTTelecomScraper
from src.scrapers.viettel_careers import ViettelCareersScraper
from src.scrapers.community_tech import CommunityTechScraper

__all__ = [
    "BaseScraper",
    "FPTTelecomScraper",
    "ViettelCareersScraper",
    "CommunityTechScraper",
]
