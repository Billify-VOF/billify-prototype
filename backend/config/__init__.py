"""
Configuration package for the Billify project.
Contains all Django settings and environment configurations.
"""
from .settings.celery import app as celery_app

__version__ = '1.0.0'

__all__ = ('celery_app',)
