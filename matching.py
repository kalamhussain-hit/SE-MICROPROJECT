import re
from datetime import datetime
from difflib import SequenceMatcher

# Weights for Smart Matching
WEIGHT_CATEGORY = 0.30
WEIGHT_LOCATION = 0.25
WEIGHT_DATE = 0.20
WEIGHT_DESCRIPTION = 0.25
DEFAULT_MATCH_THRESHOLD = 50.0  # Percentage threshold to qualify as a potential match

# Common campus stop words to filter out before calculating lexical description overlap
STOP_WORDS = {
    "a", "an", "the", "in", "on", "at", "by", "for", "with", "about", "against",
    "between", "into", "through", "during", "before", "after", "above", "below",
    "to", "from", "up", "down", "of", "off", "over", "under", "again", "further",
    "then", "once", "here", "there", "when", "where", "why", "how", "all", "any",
    "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor",
    "not", "only", "own", "same", "so", "than", "too", "very", "can", "will",
    "just", "should", "now", "it", "its", "is", "was", "are", "were", "this",
    "that", "these", "those", "i", "my", "me", "we", "our", "you", "your", "he",
    "she", "they", "them", "left", "found", "lost", "please"
}


def tokenize(text):
    """Tokenize and clean text into significant lowercase words."""
    if not text:
        return []
    words = re.findall(r"\b[a-zA-Z0-9_\-]+\b", text.lower())
    return [w for w in words if w not in STOP_WORDS and len(w) > 1]


def compute_category_score(cat_lost, cat_found):
    """
    Compute category similarity score (0.0 to 1.0).
    Exact match = 1.0, mismatch = 0.0.
    """
    if not cat_lost or not cat_found:
        return 0.0, "Missing Category"
    if cat_lost.strip().lower() == cat_found.strip().lower():
        return 1.0, "Exact Match"
    return 0.0, "Different Category"


def compute_location_score(loc_lost, loc_found):
    """
    Compute location similarity score (0.0 to 1.0).
    Uses token overlap and SequenceMatcher ratio.
    """
    if not loc_lost or not loc_found:
        return 0.0, "Missing Location"

    clean_lost = loc_lost.strip().lower()
    clean_found = loc_found.strip().lower()

    if clean_lost == clean_found:
        return 1.0, "Exact Match"

    # Token overlap
    tokens_lost = set(tokenize(clean_lost))
    tokens_found = set(tokenize(clean_found))

    if tokens_lost and tokens_found:
        intersection = tokens_lost.intersection(tokens_found)
        union = tokens_lost.union(tokens_found)
        jaccard = len(intersection) / len(union) if union else 0.0
    else:
        jaccard = 0.0

    # Sequence string similarity
    seq_ratio = SequenceMatcher(None, clean_lost, clean_found).ratio()

    score = max(jaccard, seq_ratio)

    if score >= 0.8:
        qual = "High Location Match"
    elif score >= 0.4:
        qual = "Partial / Nearby Location"
    else:
        qual = "Different Location"

    return round(score, 2), qual


def compute_date_score(date_lost, date_found):
    """
    Compute date proximity score (0.0 to 1.0).
    Same day = 1.0.
    1-2 days diff = 0.85.
    3-5 days diff = 0.65.
    6-10 days diff = 0.40.
    11-20 days diff = 0.20.
    >20 days diff = 0.05.
    """
    if not date_lost or not date_found:
        return 0.0, "Unknown Date"

    try:
        if isinstance(date_lost, str):
            d1 = datetime.strptime(date_lost.strip(), "%Y-%m-%d").date()
        else:
            d1 = date_lost
        if isinstance(date_found, str):
            d2 = datetime.strptime(date_found.strip(), "%Y-%m-%d").date()
        else:
            d2 = date_found
    except (ValueError, TypeError):
        return 0.0, "Invalid Date Format"

    days_diff = abs((d1 - d2).days)

    if days_diff == 0:
        return 1.0, "Same Day"
    elif days_diff <= 2:
        return 0.85, f"Within {days_diff} Day(s)"
    elif days_diff <= 5:
        return 0.65, f"Within {days_diff} Days"
    elif days_diff <= 10:
        return 0.40, f"Within {days_diff} Days"
    elif days_diff <= 20:
        return 0.20, f"{days_diff} Days Apart"
    else:
        return 0.05, f"{days_diff}+ Days Apart"


def compute_description_score(desc_lost, desc_found, title_lost="", title_found=""):
    """
    Compute text description and title similarity score (0.0 to 1.0).
    Combines title matching and description keyword overlap.
    """
    full_text_lost = f"{title_lost} {desc_lost}".strip()
    full_text_found = f"{title_found} {desc_found}".strip()

    if not full_text_lost or not full_text_found:
        return 0.0, "Missing Description"

    tokens_lost = set(tokenize(full_text_lost))
    tokens_found = set(tokenize(full_text_found))

    if not tokens_lost or not tokens_found:
        return 0.0, "Insufficient Keywords"

    overlap = tokens_lost.intersection(tokens_found)
    smaller_len = min(len(tokens_lost), len(tokens_found))
    overlap_ratio = len(overlap) / smaller_len if smaller_len > 0 else 0.0

    seq_ratio = SequenceMatcher(None, full_text_lost.lower(), full_text_found.lower()).ratio()

    # Blend token overlap and sequence ratio
    score = (overlap_ratio * 0.6) + (seq_ratio * 0.4)
    score = min(1.0, max(0.0, score))

    if score >= 0.7:
        qual = "High Similarity"
    elif score >= 0.35:
        qual = "Moderate Similarity"
    elif score > 0.1:
        qual = "Low Similarity"
    else:
        qual = "Minimal Match"

    return round(score, 2), qual


def calculate_match_details(lost_item, found_item):
    """
    Calculate weighted multi-attribute match score and explainable breakdown.
    Attributes:
      - Category: 30%
      - Location: 25%
      - Date proximity: 20%
      - Description: 25%
    Returns:
      total_score (float 0-100), breakdown (dict), explanation (str)
    """
    cat_score, cat_reason = compute_category_score(
        lost_item.get("category"), found_item.get("category")
    )
    loc_score, loc_reason = compute_location_score(
        lost_item.get("location"), found_item.get("location")
    )
    date_score, date_reason = compute_date_score(
        lost_item.get("date"), found_item.get("date")
    )
    desc_score, desc_reason = compute_description_score(
        lost_item.get("description", ""),
        found_item.get("description", ""),
        lost_item.get("title", ""),
        found_item.get("title", "")
    )

    weighted_total = (
        (cat_score * WEIGHT_CATEGORY) +
        (loc_score * WEIGHT_LOCATION) +
        (date_score * WEIGHT_DATE) +
        (desc_score * WEIGHT_DESCRIPTION)
    ) * 100.0

    total_score = round(min(100.0, max(0.0, weighted_total)), 1)

    breakdown = {
        "category": {
            "score": round(cat_score * 100, 1),
            "weight": int(WEIGHT_CATEGORY * 100),
            "reason": cat_reason
        },
        "location": {
            "score": round(loc_score * 100, 1),
            "weight": int(WEIGHT_LOCATION * 100),
            "reason": loc_reason
        },
        "date": {
            "score": round(date_score * 100, 1),
            "weight": int(WEIGHT_DATE * 100),
            "reason": date_reason
        },
        "description": {
            "score": round(desc_score * 100, 1),
            "weight": int(WEIGHT_DESCRIPTION * 100),
            "reason": desc_reason
        }
    }

    reason_summary = (
        f"Category: {cat_reason} | "
        f"Location: {loc_reason} | "
        f"Date: {date_reason} | "
        f"Description: {desc_reason}"
    )

    return total_score, breakdown, reason_summary


def find_matches_for_item(item, candidate_items, threshold=DEFAULT_MATCH_THRESHOLD):
    """
    Compare a given item (Lost or Found) against a list of candidates of the opposite type.
    Returns ranked list of matches meeting or exceeding threshold.
    """
    matches = []
    item_type = item.get("item_type")

    for candidate in candidate_items:
        # Must be opposite types (Lost vs Found)
        if candidate.get("item_type") == item_type:
            continue
        # Avoid matching with oneself if reported by same user
        if item.get("reported_by") and candidate.get("reported_by") == item.get("reported_by"):
            continue

        if item_type == "Lost":
            lost_ref = item
            found_ref = candidate
        else:
            lost_ref = candidate
            found_ref = item

        score, breakdown, reason = calculate_match_details(lost_ref, found_ref)

        if score >= threshold:
            matches.append({
                "lost_item": lost_ref,
                "found_item": found_ref,
                "candidate_item": candidate,
                "score": score,
                "breakdown": breakdown,
                "reason": reason
            })

    # Sort descending by score
    matches.sort(key=lambda m: m["score"], reverse=True)
    return matches

