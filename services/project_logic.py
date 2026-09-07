import time
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Sanfaani-SEO-Auditor/1.0 (+https://sanfaani.com)'
}

def is_valid_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return bool(parsed.scheme in ('http', 'https') and parsed.netloc)
    except Exception:
        return False

def audit_url(url: str) -> dict:
    deductions = []
    score = 100

    start_time = time.time()
    try:
        response = requests.get(url, headers=HEADERS, timeout=8, allow_redirects=True)
        response_time = round((time.time() - start_time) * 1000, 2)
        status_code = response.status_code
    except requests.exceptions.RequestException as e:
        return {
            'status_code': 0,
            'response_time_ms': 0,
            'title': None,
            'meta_description': None,
            'h1_count': 0,
            'images_without_alt': 0,
            'total_images': 0,
            'broken_links_count': 0,
            'audit_score': 0,
            'deductions': ["Website unreachable or timed out."]
        }

    if status_code != 200:
        score -= 40
        deductions.append(f"HTTP response status was {status_code} instead of 200 (-40).")

    soup = BeautifulSoup(response.text, 'html.parser')

    # 1. Page Title Check
    title_tag = soup.find('title')
    title = title_tag.text.strip() if title_tag and title_tag.text else None
    if not title:
        score -= 15
        deductions.append("Missing <title> tag (-15).")
    elif len(title) < 10 or len(title) > 70:
        score -= 5
        deductions.append(f"Title length ({len(title)} chars) is outside optimal SEO range of 10-70 chars (-5).")

    # 2. Meta Description Check
    meta_desc_tag = soup.find('meta', attrs={'name': lambda x: x and x.lower() == 'description'})
    meta_desc = meta_desc_tag.get('content', '').strip() if meta_desc_tag else None
    if not meta_desc:
        score -= 15
        deductions.append("Missing meta description (-15).")
    elif len(meta_desc) < 50 or len(meta_desc) > 160:
        score -= 5
        deductions.append(f"Meta description ({len(meta_desc)} chars) outside recommended 50-160 chars (-5).")

    # 3. Headings Structure Check (H1)
    h1_tags = soup.find_all('h1')
    h1_count = len(h1_tags)
    if h1_count == 0:
        score -= 15
        deductions.append("No <h1> heading found on the page (-15).")
    elif h1_count > 1:
        score -= 5
        deductions.append(f"Multiple <h1> tags found ({h1_count}). Best practice is exactly 1 (-5).")

    # 4. Image Alt Attribute Check
    images = soup.find_all('img')
    total_images = len(images)
    images_without_alt = sum(1 for img in images if not img.get('alt') or not img.get('alt').strip())
    if images_without_alt > 0:
        penalty = min(15, images_without_alt * 3)
        score -= penalty
        deductions.append(f"{images_without_alt} image(s) missing alt text (-{penalty}).")

    # 5. Check up to 5 Internal Links for Broken Status (to keep runtime fast)
    parsed_root = urlparse(url)
    anchors = soup.find_all('a', href=True)
    internal_links = []
    for a in anchors:
        full_link = urljoin(url, a['href'])
        p = urlparse(full_link)
        if p.netloc == parsed_root.netloc and full_link not in internal_links:
            internal_links.append(full_link)
        if len(internal_links) >= 5:
            break

    broken_links = 0
    for link in internal_links:
        try:
            head_res = requests.head(link, headers=HEADERS, timeout=4, allow_redirects=True)
            if head_res.status_code >= 400:
                broken_links += 1
        except requests.RequestException:
            broken_links += 1

    if broken_links > 0:
        penalty = broken_links * 5
        score -= penalty
        deductions.append(f"{broken_links} broken internal link(s) detected (-{penalty}).")

    score = max(0, min(100, score))

    return {
        'status_code': status_code,
        'response_time_ms': response_time,
        'title': title,
        'meta_description': meta_desc,
        'h1_count': h1_count,
        'images_without_alt': images_without_alt,
        'total_images': total_images,
        'broken_links_count': broken_links,
        'audit_score': score,
        'deductions': deductions
    }