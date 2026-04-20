import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

def analyze_page(url):
    """
    Analyzes a webpage and returns SEO metrics.
    """
    
    try:
        # Send request to get webpage
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, timeout=15, headers=headers)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # ----- TITLE ANALYSIS -----
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
            title_length = len(title)
        else:
            title = "No title found"
            title_length = 0
        
        # ----- META DESCRIPTION -----
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            meta_description = meta_desc.get("content").strip()
            meta_desc_length = len(meta_description)
        else:
            meta_description = "No meta description found"
            meta_desc_length = 0
        
        # ----- HEADINGS COUNT -----
        headings = {}
        for i in range(1, 7):
            tag = f"h{i}"
            headings[tag] = len(soup.find_all(tag))
        
        # ----- IMAGES ANALYSIS -----
        images = soup.find_all("img")
        total_images = len(images)
        
        images_with_alt = 0
        images_without_alt = 0
        
        for img in images:
            if img.get("alt"):
                images_with_alt += 1
            else:
                images_without_alt += 1
        
        # ----- LINKS ANALYSIS -----
        internal_links = set()
        external_links = set()
        base_domain = urlparse(url).netloc
        
        for link in soup.find_all("a", href=True):
            href = urljoin(url, link['href'])
            link_domain = urlparse(href).netloc
            
            if not link_domain or link_domain == 'javascript:':
                continue
                
            if link_domain == base_domain:
                internal_links.add(href)
            elif link_domain:
                external_links.add(href)
        
        # ----- SEO SCORE CALCULATION -----
        score = 100
        
        # Title checks
        if title == "No title found":
            score -= 30
        elif title_length < 30 or title_length > 60:
            score -= 10
            
        # Meta description checks
        if meta_description == "No meta description found":
            score -= 30
        elif meta_desc_length < 50 or meta_desc_length > 160:
            score -= 10
            
        # Image alt text checks
        if total_images > 0:
            alt_percentage = (images_with_alt / total_images) * 100
            if alt_percentage < 50:
                score -= 20
            elif alt_percentage < 80:
                score -= 10
                
        # Heading checks
        if headings['h1'] == 0:
            score -= 15
        if headings['h1'] > 1:
            score -= 10
            
        # Ensure score doesn't go below 0
        score = max(0, score)
        
        # Return all results
        return {
            "URL": url,
            "Title": title,
            "Title_Length": title_length,
            "Meta_Description": meta_description,
            "Meta_Description_Length": meta_desc_length,
            "Headings": headings,
            "Total_Images": total_images,
            "Images_With_Alt": images_with_alt,
            "Images_Without_Alt": images_without_alt,
            "Internal_Links_Count": len(internal_links),
            "External_Links_Count": len(external_links),
            "SEO_Score": score
        }
    
    except requests.exceptions.RequestException as e:
        return {
            "Error": f"Could not fetch the URL: {str(e)}",
            "URL": url
        }
