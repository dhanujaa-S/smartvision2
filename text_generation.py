"""
Module 6: Text Generation
---------------------------
Converts PositionedDetection objects into natural-language sentences,
in English or Tamil, ready to hand off to the Text-to-Speech module.

Keeps only the most relevant / closest detection(s) per "announcement" so
the user isn't flooded with sentences for every object in frame.
"""

from .position_analysis import PositionedDetection

_DISTANCE_PRIORITY = {"near": 0, "medium": 1, "far": 2}

_TEMPLATES_EN = {
    ("center", "near"): "{label} right in front of you.",
    ("center", "medium"): "{label} ahead.",
    ("center", "far"): "{label} far ahead.",
    ("left", "near"): "{label} close on your left.",
    ("left", "medium"): "{label} on your left.",
    ("left", "far"): "{label} far to your left.",
    ("right", "near"): "{label} close on your right.",
    ("right", "medium"): "{label} on your right.",
    ("right", "far"): "{label} far to your right.",
}

_TEMPLATES_TA = {
    ("center", "near"): "{label} உங்கள் முன்னால் இருக்கிறது.",
    ("center", "medium"): "{label} முன்னால் இருக்கிறது.",
    ("center", "far"): "{label} தூரத்தில் முன்னால் இருக்கிறது.",
    ("left", "near"): "{label} உங்கள் இடதுபுறம் அருகில் இருக்கிறது.",
    ("left", "medium"): "{label} உங்கள் இடதுபுறம் இருக்கிறது.",
    ("left", "far"): "{label} உங்கள் இடதுபுறம் தூரத்தில் இருக்கிறது.",
    ("right", "near"): "{label} உங்கள் வலதுபுறம் அருகில் இருக்கிறது.",
    ("right", "medium"): "{label} உங்கள் வலதுபுறம் இருக்கிறது.",
    ("right", "far"): "{label} உங்கள் வலதுபுறம் தூரத்தில் இருக்கிறது.",
}


def generate_sentence(pd: PositionedDetection, language="en"):
    templates = _TEMPLATES_EN if language == "en" else _TEMPLATES_TA
    key = (pd.horizontal, pd.distance)
    template = templates.get(key, "{label} detected.")
    return template.format(label=pd.label)


def generate_announcements(positioned_detections, language="en", max_announcements=2):
    """
    Picks the closest / most important detections and turns each into a
    sentence. Limiting max_announcements keeps the voice guidance from
    talking over itself when many objects are in frame at once.
    """
    if not positioned_detections:
        return []

    ranked = sorted(
        positioned_detections,
        key=lambda d: (_DISTANCE_PRIORITY.get(d.distance, 3), d.horizontal != "center"),
    )
    top = ranked[:max_announcements]
    return [generate_sentence(d, language=language) for d in top]
