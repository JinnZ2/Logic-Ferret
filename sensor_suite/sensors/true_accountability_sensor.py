# sensor_suite/sensors/true_accountability_sensor.py

from typing import Tuple, Dict
import re

# Genuine accountability patterns
ACCOUNTABILITY_PATTERNS = [
    r"i was wrong about",
    r"i made a mistake",
    r"my error was",
    r"i take full responsibility",
    r"i should have",
    r"i failed to",
    r"this is on me",
    r"i own this failure"
]

# Giving credit to others
CREDIT_SHARING_PATTERNS = [
    r"the team deserves credit",
    r"thanks to my colleagues", 
    r"my staff made this possible",
    r"others contributed",
    r"couldn't have done it without",
    r"team effort resulted",
    r"collaborative success"
]

# Intellectual humility
HUMILITY_PATTERNS = [
    r"i don't know",
    r"i'm not sure",
    r"i need to learn more",
    r"i was mistaken",
    r"let me find out",
    r"i'll get back to you",
    r"that's a good question",
    r"i hadn't considered that"
]

# Evidence of learning/adaptation
LEARNING_PATTERNS = [
    r"i've learned that",
    r"experience taught me",
    r"i now understand", 
    r"this changed my view",
    r"i adapted by",
    r"feedback showed me",
    r"data indicated i was wrong"
]

def assess(text: str) -> Tuple[float, Dict[str, int]]:
    flags = {}
    lower_text = text.lower()
    
    # Count accountability patterns
    accountability_hits = 0
    for pattern in ACCOUNTABILITY_PATTERNS:
        matches = len(re.findall(pattern, lower_text))
        if matches > 0:
            accountability_hits += matches
    
    # Count credit sharing
    credit_sharing_hits = 0
    for pattern in CREDIT_SHARING_PATTERNS:
        matches = len(re.findall(pattern, lower_text))
        if matches > 0:
            credit_sharing_hits += matches
    
    # Count humility markers
    humility_hits = 0
    for pattern in HUMILITY_PATTERNS:
        matches = len(re.findall(pattern, lower_text))
        if matches > 0:
            humility_hits += matches
    
    # Count learning indicators
    learning_hits = 0
    for pattern in LEARNING_PATTERNS:
        matches = len(re.findall(pattern, lower_text))
        if matches > 0:
            learning_hits += matches
    
    total_accountability = accountability_hits + credit_sharing_hits + humility_hits + learning_hits
    
    # Higher score = more accountability (good)
    score = min(total_accountability / 8.0, 1.0)
    
    flags["Takes Responsibility"] = accountability_hits
    flags["Shares Credit"] = credit_sharing_hits
    flags["Shows Humility"] = humility_hits
    flags["Demonstrates Learning"] = learning_hits
    flags["Total Accountability Score"] = f"{score:.2f}"
    
    return score, flags


# sensor_suite/sensors/meritocracy_detector.py

from typing import Tuple, Dict
import re

# Actual competence indicators
COMPETENCE_PATTERNS = [
    r"here's the data",
    r"evidence shows",
    r"results indicate", 
    r"testing revealed",
    r"measurements confirm",
    r"proven track record",
    r"demonstrable results",
    r"verifiable outcomes"
]

# Appeals to false authority instead of merit
FALSE_AUTHORITY_PATTERNS = [
    r"trust me, i'm an expert",
    r"because i said so",
    r"my credentials speak",
    r"i'm the authority",
    r"my position gives me",
    r"years of experience prove",
    r"my degree means",
    r"as someone with a title"
]

# Nepotism/favoritism indicators  
FAVORITISM_PATTERNS = [
    r"old friend of mine",
    r"family connection",
    r"went to school together",
    r"longtime associate", 
    r"personal relationship",
    r"inner circle",
    r"handpicked by me"
]

# Merit-based decision making
MERIT_PATTERNS = [
    r"best qualified candidate",
    r"highest performance",
    r"strongest results",
    r"most capable person",
    r"earned this position",
    r"proven ability",
    r"demonstrated competence",
    r"objective evaluation"
]

def assess(text: str) -> Tuple[float, Dict[str, int]]:
    flags = {}
    lower_text = text.lower()
    
    # Count competence indicators (positive)
    competence_hits = 0
    for pattern in COMPETENCE_PATTERNS:
        matches = len(re.findall(pattern, lower_text))
        if matches > 0:
            competence_hits += matches
    
    # Count merit-based language (positive)
    merit_hits = 0
    for pattern in MERIT_PATTERNS:
        matches = len(re.findall(pattern, lower_text))
        if matches > 0:
            merit_hits += matches
    
    # Count false authority appeals (negative)
    false_authority_hits = 0
    for pattern in FALSE_AUTHORITY_PATTERNS:
        matches = len(re.findall(pattern, lower_text))
        if matches > 0:
            false_authority_hits += matches
    
    # Count favoritism indicators (negative)
    favoritism_hits = 0
    for pattern in FAVORITISM_PATTERNS:
        matches = len(re.findall(pattern, lower_text))
        if matches > 0:
            favoritism_hits += matches
    
    # Calculate meritocracy score
    positive_signals = competence_hits + merit_hits
    negative_signals = false_authority_hits + favoritism_hits
    
    # Higher positive, lower negative = better meritocracy score
    raw_score = (positive_signals - negative_signals) / max(positive_signals + negative_signals, 1)
    score = max(0.0, min(raw_score, 1.0))
    
    flags["Competence Indicators"] = competence_hits
    flags["Merit-Based Language"] = merit_hits
    flags["False Authority Appeals"] = false_authority_hits  
    flags["Favoritism Signals"] = favoritism_hits
    flags["Meritocracy Score"] = f"{score:.2f}"
    
    return score, flags
