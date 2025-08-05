"""
Educational Module for URCS Investigator Toolkit
Comprehensive educational content for mining and cryptocurrency analysis.
This module provides theoretical knowledge and defensive analysis capabilities only.
NO ACTUAL MINING, ATTACKS, OR MALICIOUS ACTIVITIES OCCUR.
"""

from .educational_suite import EducationalSuite
from .mining_education import MiningEducation
from .cybersecurity_awareness import CybersecurityAwareness
from .system_administration import SystemAdministration
from .privacy_protection import PrivacyProtection

__all__ = [
    'EducationalSuite',
    'MiningEducation', 
    'CybersecurityAwareness',
    'SystemAdministration',
    'PrivacyProtection'
]

__version__ = "1.0.0"
__author__ = "URCS Investigator Team"
__description__ = "Educational module for mining and cryptocurrency analysis"
__disclaimer__ = "FOR EDUCATIONAL PURPOSES ONLY - NO ACTUAL MINING OR ATTACKS OCCUR"