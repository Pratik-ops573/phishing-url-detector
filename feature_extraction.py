"""
Comprehensive feature extraction for phishing URL detection.

Extracts all 80 features including:
- URL string-level features (basic counts, structure)
- HTML/page-content features (requires fetching the page)
- WHOIS/domain-registration features
- DNS features
- Traffic/ranking features (approximated with neutral defaults)
"""

import re
from urllib.parse import urlparse
from datetime import datetime
import time

import requests
from bs4 import BeautifulSoup
import whois
import dns.resolver
import dns.exception


# ============================================================================
# URL-LEVEL FEATURE EXTRACTION (no external calls)
# ============================================================================

def _extract_url_features(url):
    """Extract features from URL string only."""
    features = {}

    # Basic character counts
    features["length_url"] = len(url)
    features["nb_dots"] = url.count(".")
    features["nb_hyphens"] = url.count("-")
    features["nb_at"] = url.count("@")
    features["nb_qm"] = url.count("?")
    features["nb_and"] = url.count("&")
    features["nb_eq"] = url.count("=")
    features["nb_underscore"] = url.count("_")
    features["nb_tilde"] = url.count("~")
    features["nb_percent"] = url.count("%")
    features["nb_slash"] = url.count("/")
    features["nb_colon"] = url.count(":")
    features["nb_comma"] = url.count(",")
    features["nb_semicolumn"] = url.count(";")
    features["nb_dollar"] = url.count("$")
    features["nb_space"] = url.count(" ")
    features["nb_com"] = url.lower().count(".com")

    parsed_url = urlparse(url)
    hostname = parsed_url.hostname or ""
    path = parsed_url.path or ""

    # Hostname features
    features["length_hostname"] = len(hostname)
    features["nb_www"] = hostname.count("www")
    features["nb_subdomains"] = max(hostname.count(".") - 1, 0)

    # URL structure
    features["nb_dslash"] = max(url.count("//") - 1, 0)
    features["http_in_path"] = int("http" in path.lower())
    features["https_token"] = int("https" in url.lower())

    # Digit ratios
    features["ratio_digits_url"] = (
        sum(c.isdigit() for c in url) / len(url) if len(url) > 0 else 0
    )
    features["ratio_digits_host"] = (
        sum(c.isdigit() for c in hostname) / len(hostname) if len(hostname) > 0 else 0
    )

    # Word-based features
    url_words = url.replace("/", " ").replace(".", " ").replace("-", " ").split()
    host_words = hostname.replace(".", " ").replace("-", " ").split()
    path_words = path.replace("/", " ").replace("-", " ").split()

    features["length_words_raw"] = len(url_words)
    features["shortest_words_raw"] = min([len(w) for w in url_words], default=0)
    features["shortest_word_host"] = min([len(w) for w in host_words], default=0)
    features["shortest_word_path"] = min([len(w) for w in path_words], default=0)
    features["longest_words_raw"] = max([len(w) for w in url_words], default=0)
    features["longest_word_host"] = max([len(w) for w in host_words], default=0)
    features["longest_word_path"] = max([len(w) for w in path_words], default=0)

    features["avg_words_raw"] = (
        sum(len(w) for w in url_words) / len(url_words) if url_words else 0
    )
    features["avg_word_host"] = (
        sum(len(w) for w in host_words) / len(host_words) if host_words else 0
    )
    features["avg_word_path"] = (
        sum(len(w) for w in path_words) / len(path_words) if path_words else 0
    )

    # Character repetition
    features["char_repeat"] = max([url.count(c) for c in set(url)], default=0)

    # Domain/TLD features
    features["prefix_suffix"] = int("-" in hostname)

    shortening_services = [
        "bit.ly", "tinyurl.com", "goo.gl", "t.co", "ow.ly", 
        "is.gd", "buff.ly", "adf.ly", "bit.do"
    ]
    features["shortening_service"] = int(
        any(s in hostname.lower() for s in shortening_services)
    )

    suspicious_tlds = [".tk", ".ml", ".ga", ".cf", ".gq", ".top", ".xyz", ".club"]
    features["suspecious_tld"] = int(
        any(hostname.lower().endswith(t) for t in suspicious_tlds)
    )

    # IP address detection
    features["ip"] = int(
        re.match(r"^\d{1,3}(\.\d{1,3}){3}$", hostname) is not None
    )

    # Port detection
    features["port"] = int(parsed_url.port is not None)

    # TLD in path/subdomain
    hostname_parts = hostname.split(".")
    tld = "." + hostname_parts[-1] if len(hostname_parts) >= 2 else ""
    features["tld_in_path"] = int(tld != "" and tld in path.lower())

    subdomain = ".".join(hostname_parts[:-2])
    features["tld_in_subdomain"] = int(tld != "" and tld in subdomain.lower())
    features["abnormal_subdomain"] = int(len(hostname_parts) > 4)

    # Random domain (many consecutive digits)
    features["random_domain"] = int(bool(re.search(r"[0-9]{4,}", hostname)))

    # Punycode detection (internationalized domain names)
    features["punycode"] = int("xn--" in hostname.lower())

    # Path extension (.pdf, .zip, etc.)
    features["path_extension"] = int(bool(re.search(r"\.\w{2,4}$", path)))

    # Redirection detection
    features["nb_redirection"] = url.lower().count("//")
    features["nb_external_redirection"] = len(re.findall(r"http[s]?://", url.lower())) - 1

    # Brand features
    brands = [
        "google", "facebook", "paypal", "amazon", "microsoft", 
        "apple", "netflix", "instagram", "linkedin", "twitter", "bank"
    ]
    url_lower = url.lower()
    hostname_lower = hostname.lower()
    path_lower = path.lower()

    features["domain_in_brand"] = int(any(b in hostname_lower for b in brands))
    features["brand_in_subdomain"] = int(any(b in subdomain.lower() for b in brands))
    features["brand_in_path"] = int(any(b in path_lower for b in brands))

    # Phishing hints
    suspicious_words = [
        "login", "signin", "verify", "verification", "account", "update", 
        "secure", "security", "confirm", "password", "bank", "paypal"
    ]
    features["phish_hints"] = sum(w in url_lower for w in suspicious_words)

    return features


# ============================================================================
# HTML/PAGE-CONTENT FEATURE EXTRACTION
# ============================================================================

def _extract_html_features(url):
    """
    Fetch the page and extract HTML/DOM-based features.
    Returns dict of features; missing features are set to 0.
    Also returns a flag indicating if the fetch succeeded.
    """
    features = {
        "nb_hyperlinks": 0,
        "ratio_intHyperlinks": 0,
        "ratio_extHyperlinks": 0,
        "nb_extCSS": 0,
        "ratio_extRedirection": 0,
        "ratio_extErrors": 0,
        "login_form": 0,
        "external_favicon": 0,
        "links_in_tags": 0,
        "ratio_intMedia": 0,
        "ratio_extMedia": 0,
        "iframe": 0,
        "popup_window": 0,
        "safe_anchor": 0,
        "onmouseover": 0,
        "right_clic": 0,
        "empty_title": 0,
        "domain_in_title": 0,
        "domain_with_copyright": 0,
    }
    
    fetch_succeeded = False
    
    try:
        # Fetch page with timeout and spoofed User-Agent
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, timeout=5, verify=True, headers=headers, allow_redirects=True)
        response.raise_for_status()
        
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        fetch_succeeded = True
        
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname or ""
        
        # ===== Hyperlinks =====
        links = soup.find_all("a", href=True)
        features["nb_hyperlinks"] = len(links)
        
        if len(links) > 0:
            internal = sum(
                1 for link in links 
                if _is_internal_link(link["href"], hostname)
            )
            external = len(links) - internal
            features["ratio_intHyperlinks"] = internal / len(links)
            features["ratio_extHyperlinks"] = external / len(links)
        
        # ===== External CSS =====
        stylesheets = soup.find_all("link", rel="stylesheet", href=True)
        features["nb_extCSS"] = len(stylesheets)
        
        # ===== External Redirections =====
        meta_refresh = soup.find("meta", attrs={"http-equiv": "refresh"})
        features["ratio_extRedirection"] = int(meta_refresh is not None)
        
        # ===== External Errors =====
        images = soup.find_all("img", src=True)
        ext_images = sum(1 for img in images if not _is_internal_link(img["src"], hostname))
        features["ratio_extErrors"] = ext_images / len(images) if images else 0
        
        # ===== Login Form =====
        forms = soup.find_all("form")
        for form in forms:
            password_input = form.find("input", attrs={"type": "password"})
            if password_input:
                features["login_form"] = 1
                break
        
        # ===== External Favicon =====
        favicon = soup.find("link", rel="icon") or soup.find("link", rel="shortcut icon")
        if favicon and "href" in favicon.attrs:
            favicon_url = favicon["href"]
            if not _is_internal_link(favicon_url, hostname):
                features["external_favicon"] = 1
        
        # ===== Links in Tags =====
        anchor_text = " ".join([link.get_text() for link in links])
        features["links_in_tags"] = int(any(word in anchor_text.lower() for word in ["click", "here", "download"]))
        
        # ===== Media (images, videos) =====
        iframes = soup.find_all("iframe")
        features["iframe"] = int(len(iframes) > 0)
        
        # Media resources
        videos = soup.find_all(["video", "source"])
        int_media = len([v for v in videos if _is_internal_link(v.get("src", ""), hostname)])
        ext_media = len(videos) - int_media
        features["ratio_intMedia"] = int_media / len(videos) if videos else 0
        features["ratio_extMedia"] = ext_media / len(videos) if videos else 0
        
        # ===== Popup =====
        script_tags = soup.find_all("script")
        popup_keywords = ["window.open", "alert", "confirm", "prompt"]
        features["popup_window"] = int(
            any(keyword in "".join([s.string or "" for s in script_tags if s.string]).lower() 
                for keyword in popup_keywords)
        )
        
        # ===== Safe Anchor =====
        safe_anchors = sum(
            1 for link in links 
            if link.get("target") == "_blank" and link.get("rel")
        )
        features["safe_anchor"] = int(safe_anchors > 0)
        
        # ===== onMouseOver =====
        features["onmouseover"] = sum(
            1 for elem in soup.find_all() if elem.get("onmouseover")
        )
        
        # ===== Right Click =====
        features["right_clic"] = int(any(
            "contextmenu" in str(script) or "oncontextmenu" in str(html).lower()
            for script in script_tags
        ))
        
        # ===== Title Features =====
        title = soup.find("title")
        if title and title.string:
            title_text = title.string.lower()
            features["empty_title"] = 0
            features["domain_in_title"] = int(hostname in title_text)
        else:
            features["empty_title"] = 1
        
        # ===== Copyright & Domain in Page =====
        page_text = soup.get_text().lower()
        features["domain_with_copyright"] = int(
            ("©" in page_text or "&copy;" in html.lower()) and hostname in page_text
        )
        
    except (requests.RequestException, requests.Timeout, ConnectionError, Exception):
        # Page fetch failed; all features stay at their default (0) values
        pass
    
    return features, fetch_succeeded


def _is_internal_link(link, hostname):
    """Check if a link (href/src) is internal to the given hostname."""
    if link.startswith("#") or link.startswith("javascript:") or link.startswith("mailto:"):
        return True
    
    if link.startswith("http"):
        link_host = urlparse(link).hostname or ""
        return link_host.lower() == hostname.lower()
    
    # Relative URLs are internal
    return True


# ============================================================================
# WHOIS FEATURE EXTRACTION
# ============================================================================

def _extract_whois_features(url):
    """
    Extract WHOIS-based features: domain age, registration length, registered.
    Returns dict with whois_registered_domain, domain_registration_length, domain_age.
    Sentinel value -1 indicates unknown/unavailable.
    """
    features = {
        "whois_registered_domain": -1,
        "domain_registration_length": -1,
        "domain_age": -1,
    }
    
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname or ""
    
    # Extract just the domain (no subdomain)
    parts = hostname.split(".")
    if len(parts) >= 2:
        domain = ".".join(parts[-2:])
    else:
        domain = hostname
    
    try:
        w = whois.whois(domain)
        
        # Check if registered
        if w and (w.creation_date or w.registrar):
            features["whois_registered_domain"] = 1
            
            # Domain age
            creation_date = w.creation_date
            if isinstance(creation_date, list):
                creation_date = creation_date[0]
            
            if creation_date:
                age_days = (datetime.now() - creation_date).days
                features["domain_age"] = max(0, age_days)
            
            # Registration length
            expiration_date = w.expiration_date
            if isinstance(expiration_date, list):
                expiration_date = expiration_date[0]
            
            if expiration_date:
                reg_length_days = (expiration_date - creation_date).days if creation_date else -1
                features["domain_registration_length"] = max(0, reg_length_days) if reg_length_days > 0 else -1
        else:
            features["whois_registered_domain"] = 0
    
    except Exception:
        # WHOIS lookup failed; return -1 sentinel
        pass
    
    return features


# ============================================================================
# DNS FEATURE EXTRACTION
# ============================================================================

def _extract_dns_features(url):
    """
    Check if DNS A record resolves for the domain.
    Returns dict with dns_record (0 or 1).
    """
    features = {"dns_record": 0}
    
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname or ""
    
    if not hostname:
        return features
    
    try:
        dns.resolver.resolve(hostname, "A", lifetime=3)
        features["dns_record"] = 1
    except (dns.exception.DNSException, Exception):
        features["dns_record"] = 0
    
    return features


# ============================================================================
# TRAFFIC/RANK FEATURES (APPROXIMATED WITH NEUTRAL DEFAULTS)
# ============================================================================

def _extract_traffic_features():
    """
    Traffic and ranking features are approximated with neutral/"unknown" values.
    These historically came from Alexa (now defunct) or paywalled APIs.
    
    Using default value 0 (legitimate-leaning) for all, as this is the neutral
    placeholder in training data.
    
    NOTE: This is a limitation of the free tier. For production, consider:
    - Google PageRank API (deprecated)
    - OpenPageRank (free tier available)
    - SimilarWeb API (paid)
    """
    return {
        "web_traffic": 0,        # Unknown/approximated
        "google_index": 0,       # Unknown/approximated
        "page_rank": 0,          # Unknown/approximated
        "statistical_report": 0, # Unknown/approximated
    }


# ============================================================================
# MAIN EXTRACTION FUNCTION
# ============================================================================

def extract_all_features(url):
    """
    Extract all 80 features for the phishing detection model.
    
    Args:
        url (str): The URL to analyze
    
    Returns:
        dict: Feature dict with all keys matching the model's expected features
        bool: Whether page content fetch succeeded (for UI notification)
    
    Raises:
        ValueError: If URL is empty or invalid
    """
    if not url or not isinstance(url, str):
        raise ValueError("URL must be a non-empty string")
    
    # Normalize URL
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    
    # Extract features from all sources
    url_features = _extract_url_features(url)
    html_features, fetch_succeeded = _extract_html_features(url)
    whois_features = _extract_whois_features(url)
    dns_features = _extract_dns_features(url)
    traffic_features = _extract_traffic_features()
    
    # Merge all features
    all_features = {}
    all_features.update(url_features)
    all_features.update(html_features)
    all_features.update(whois_features)
    all_features.update(dns_features)
    all_features.update(traffic_features)
    
    return all_features, fetch_succeeded


def build_feature_vector(features_dict, feature_names):
    """
    Build a feature vector in the exact order expected by the model.
    
    Args:
        features_dict (dict): Feature dict from extract_all_features()
        feature_names (list): Feature names list from joblib.load('phishing_url_features.pkl')
    
    Returns:
        list: Feature vector in the correct order for model prediction
    
    Raises:
        ValueError: If any expected feature is missing
    """
    vector = []
    missing = []
    
    for fname in feature_names:
        if fname not in features_dict:
            missing.append(fname)
        else:
            vector.append(features_dict[fname])
    
    if missing:
        raise ValueError(
            f"Missing {len(missing)} expected features: {missing}"
        )
    
    return vector
