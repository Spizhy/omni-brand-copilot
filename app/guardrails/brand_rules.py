from typing import List, Dict

BANNED_BUZZWORDS: List[str] = [
    "game-changing",
    "game changer",
    "revolutionary",
    "disruptive",
    "silver bullet",
    "10x engineer",
    "miracle",
    "unmatched",
    "unrivaled",
    "next-gen paradigm",
    "world-class synergy"
]

COMPETITOR_DISPARAGEMENT_PHRASES: List[str] = [
    "competitors are garbage",
    "our rivals suck",
    "inferior legacy garbage",
    "clueless competition"
]

CHANNEL_MAX_CHARS: Dict[str, int] = {
    "TWITTER_THREAD": 280,  # Max per single tweet chunk
    "LINKEDIN_POST": 3000,
    "NEWSLETTER_DIGEST": 8000,
    "EXECUTIVE_ANNOUNCEMENT": 4000
}
