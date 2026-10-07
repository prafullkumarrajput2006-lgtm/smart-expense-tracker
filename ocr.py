"""
cleaned_receipt_extractor.py

Fixed version of the receipt extraction utilities:
- removes duplicate function definitions
- returns vendor, date, total, receipt_type, plain text, and line tokens
- safer amount normalization and heuristics
- grouping of OCR tokens into lines by y-center
"""

import re
from typing import Dict, Any, List, Tuple

try:
    import easyocr
except Exception:
    easyocr = None  # caller should ensure easyocr is installed


def _amount_regexps() -> List[re.Pattern]:
    """Common regex patterns to capture currency amounts in various locales."""
    patterns = [
        # e.g., Rs 1,234.56 or LKR 1,234.56 or $1,234.56 or €1.234,56
        r"(?:\b(?:rs\.?|lkr|usd|eur|gbp|inr|aed|sar)\b)?\s*[\$₹£€]?\s*([0-9]{1,3}(?:[ ,][0-9]{3})*(?:[\.,][0-9]{2})|[0-9]+(?:[\.,][0-9]{2}))",
        # plain number with decimals, allowing commas as thousands separators
        r"\b([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})|[0-9]+\.[0-9]{2})\b",
        # locales using comma as decimal separator
        r"\b([0-9]{1,3}(?:\.[0-9]{3})*(?:,[0-9]{2}))\b",
    ]
    return [re.compile(p, re.IGNORECASE) for p in patterns]


NEG_TOTAL_HINTS = {
    "subtotal",
    "sub total",
    "total items",
    "total qty",
    "total quantity",
    "total points",
    "total savings",
    "savings total",
    "tax total",
}

POS_TOTAL_HINTS = {
    "grand total",
    "net total",
    "total",
    "amount due",
    "amount payable",
    "balance due",
    "total due",
    "cash total",
    "bill total",
}


def _normalize_amount_str(s: str) -> float:
    """Convert an extracted amount string into a float, handling ,/. separators."""
    if not s:
        return 0.0
    s = s.strip()
    # Remove currency symbols and spaces
    s = re.sub(r"[^\d,.\-]", "", s)
    # If both comma and dot appear, assume comma thousands, dot decimal (en-US)
    if "," in s and "." in s:
        s = s.replace(",", "")
    else:
        # If only comma appears, assume comma is decimal separator (EU style)
        if "," in s and "." not in s:
            s = s.replace(".", "").replace(",", ".")
        else:
            # Only dots or only digits: remove commas if any
            s = s.replace(",", "")
    try:
        return float(s)
    except Exception:
        return 0.0


def _group_into_lines(detailed: List[Tuple[List[Tuple[float, float]], str, float]]) -> List[Dict[str, Any]]:
    """
    Group OCR results into logical lines using the y-center of each bounding box.
    detailed: list of tuples (bbox, text, conf) where bbox is list of 4 (x,y) points
    """
    lines: List[Dict[str, Any]] = []
    items = []
    for bbox, text, conf in detailed:
        try:
            ys = [float(p[1]) for p in bbox]
            y_center = sum(ys) / len(ys)
        except Exception:
            y_center = 0.0
        items.append({"y": y_center, "text": text.strip(), "conf": float(conf)})

    # Sort top to bottom
    items.sort(key=lambda x: x["y"])

    # Merge items that are close in y into lines
    threshold = 10  # pixels; may adjust based on DPI
    current_line: List[Dict[str, Any]] = []
    for it in items:
        if not current_line:
            current_line = [it]
            continue
        if abs(it["y"] - current_line[-1]["y"]) <= threshold:
            current_line.append(it)
        else:
            # flush current_line
            line_text = " ".join(tok["text"] for tok in current_line).strip()
            lines.append({
                "y": sum(tok["y"] for tok in current_line) / len(current_line),
                "text": line_text,
                "tokens": current_line,
            })
            current_line = [it]
    if current_line:
        line_text = " ".join(tok["text"] for tok in current_line).strip()
        lines.append({
            "y": sum(tok["y"] for tok in current_line) / len(current_line),
            "text": line_text,
            "tokens": current_line,
        })
    return lines 


def _line_has_pos_total(line_text: str) -> bool:
    lt = line_text.lower()
    if any(h in lt for h in NEG_TOTAL_HINTS):
        return False
    return any(h in lt for h in POS_TOTAL_HINTS)


def _extract_total_from_lines(lines: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Heuristically extract the grand total from OCR lines."""
    amt_patterns = _amount_regexps()
    candidates = []

    for idx, line in enumerate(lines):
        text = line.get("text", "")
        if _line_has_pos_total(text):
            # Extract last amount on the line
            found_amount = None
            for pat in amt_patterns:
                matches = list(pat.finditer(text))
                if matches:
                    # choose last match
                    found_amount = matches[-1].group(1)
            if found_amount:
                val = _normalize_amount_str(found_amount)
                candidates.append({
                    "index": idx,
                    "y": line.get("y", 0),
                    "text": text,
                    "amount_text": found_amount,
                    "amount": val,
                })

    # Prefer the candidate nearest to the bottom (highest y)
    if candidates:
        candidates.sort(key=lambda c: (c["y"], c["amount"]))
        best = candidates[-1]
        return {
            "amount": best["amount"],
            "amount_text": best["amount_text"],
            "line_index": best["index"],
            "line_text": best["text"],
            "strategy": "keyword_bottommost",
        }

    # Fallback: choose the maximum plausible amount across all lines
    max_amt = 0.0
    max_info = None
    for idx, line in enumerate(lines):
        text = line.get("text", "")
        # Skip lines that likely contain card or tax labels
        if re.search(r"\b(visa|mastercard|amex|card|auth|approval|invoice|gst|vat|tax|tel|phone)\b", text, re.I):
            continue
        for pat in amt_patterns:
            for m in pat.finditer(text):
                candidate_str = m.group(1)
                val = _normalize_amount_str(candidate_str)
                if 0.05 <= val <= 1000000:
                    if val >= max_amt:
                        max_amt = val
                        max_info = {
                            "amount": val,
                            "amount_text": candidate_str,
                            "line_index": idx,
                            "line_text": text,
                            "strategy": "global_max",
                        }
    return max_info or {}


def _detect_receipt_type(text: str, lines: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Detect the type of receipt/bill based on keywords."""
    text_lower = text.lower()

    receipt_patterns = {
        "grocery": ["supermarket", "grocery", "mart", "fresh", "organic", "vegetables", "fruits"],
        "restaurant": ["restaurant", "cafe", "coffee", "dining", "food", "bistro", "diner", "pizza", "burger", "zomato", "swiggy"],
        "fuel": ["gas", "petrol", "fuel", "diesel", "oil", "pump"],
        "utilities": ["electricity", "water", "gas bill", "utility", "kwh", "consumption", "bses"],
        "pharmacy": ["pharmacy", "medical", "rx", "prescription", "medicine"],
        "transportation": ["taxi", "uber", "ola", "lyft", "transport", "ride", "fare", "metro", "bus", "irctc"],
        "shopping": ["store", "shop", "retail", "mall", "purchase", "sale", "amazon", "flipkart", "myntra", "bigbasket"],
        "online": ["amazon", "ebay", "online", "order", "delivery", "shipping"],
    }

    detected = []
    for bill_type, keywords in receipt_patterns.items():
        if any(kw in text_lower for kw in keywords):
            detected.append(bill_type)

    if not detected:
        detected.append("general")

    return {
        "type": detected[0] if len(detected) == 1 else "mixed",
        "all_types": detected,
        "confidence": "high" if len(detected) == 1 else "medium" if detected else "low"
    }


def _extract_vendor(text: str, lines: List[Dict[str, Any]]) -> str:
    """Extract vendor/merchant name (typically first few lines, often all caps)."""
    if not lines:
        return ""

    # Check first 3 lines for a clear vendor name (prefer ALL CAPS)
    top_lines = lines[:3]
    for ln in top_lines:
        line_text = ln.get("text", "").strip()
        # If line is all uppercase and reasonably long, treat as vendor
        if line_text and line_text.isupper() and len(line_text) > 3:
            clean = re.sub(r'[^A-Z0-9\s\-&]', '', line_text).strip()
            if len(clean) >= 2:
                return clean

    # Fallback: choose first non-empty line and return cleaned text (full line)
    for ln in top_lines:
        t = ln.get("text", "").strip()
        if len(t) > 2:
            # remove noise characters at ends
            t_clean = re.sub(r'^[^A-Za-z0-9]+|[^A-Za-z0-9]+$', '', t)
            return t_clean

    return ""


def _extract_date(text: str) -> str:
    """Extract date from receipt text using common date formats."""
    patterns = [
        r'\b(\d{4}[-/]\d{2}[-/]\d{2})\b',  # YYYY-MM-DD
        r'\b(\d{2}[-/]\d{2}[-/]\d{4})\b',  # DD-MM-YYYY or MM-DD-YYYY
        r'\b(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})\b',  # 15 Jan 2025
        r'\b(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})\b',  # 15/01/2025 or 15-01-25
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return ""


def extract_text_and_fields(image_path: str) -> Dict[str, Any]:
    """
    Run EasyOCR and return structured data and parsed fields:
    {
        "text": plain_text,
        "lines": [ { "y":..., "text":..., "tokens": [...] }, ... ],
        "fields": {
            "total": {...} or {},
            "receipt_type": {...},
            "vendor": "...",
            "date": "..."
        }
    }
    """
    if easyocr is None:
        raise RuntimeError("easyocr library not available. Install via `pip install easyocr`.")

    # Create reader with English support; adjust languages if needed
    reader = easyocr.Reader(['en'], gpu=False)  # set gpu=True if GPU available

    # Read text (detail=1 returns list of (bbox, text, conf))
    detailed = reader.readtext(image_path, detail=1)  # list of tuples
    # In some EasyOCR versions, readtext returns list of (bbox, text) when detail=0; this code assumes detail=1.

    # Build plain text joined by newline for easier regex searches
    plain_text = "\n".join([t for (_, t, _) in detailed])
    lines = _group_into_lines(detailed)
    total_info = _extract_total_from_lines(lines)
    receipt_type = _detect_receipt_type(plain_text, lines)
    vendor = _extract_vendor(plain_text, lines)
    date = _extract_date(plain_text)

    return {
        "text": plain_text,
        "lines": lines,
        "fields": {
            "total": total_info,
            "receipt_type": receipt_type,
            "vendor": vendor,
            "date": date,
        },
    }


def extract_text_from_image(image_path: str) -> str:
    """
    Backward-compatible helper that returns only the flattened text.
    """
    try:
        data = extract_text_and_fields(image_path)
        return data.get("text", "")
    except Exception as e:
        return f"Error: {str(e)}"
