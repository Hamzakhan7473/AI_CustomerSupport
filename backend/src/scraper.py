import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def scrape_page(url: str) -> tuple[str | None, list[str]]:
    """
    Scrapes a single page for its text content and finds all internal links.

    Args:
        url: The URL of the page to scrape.

    Returns:
        A tuple containing the cleaned text and a list of internal links.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove script, style, nav, and footer elements for cleaner text
        for element in soup(["script", "style", "nav", "footer"]):
            element.decompose()

        # Extract clean text
        text = soup.get_text(separator='\n', strip=True)

        # Find all internal links
        internal_links = []
        for a_tag in soup.find_all('a', href=True):
            link = a_tag['href']
            # Join relative links with the base URL
            full_link = urljoin(url, link)
            # Ensure the link belongs to the aven.com domain
            if urlparse(full_link).netloc == 'www.aven.com':
                internal_links.append(full_link)

        return text, internal_links

    except requests.RequestException as e:
        print(f"Error scraping {url}: {e}")
        return None, []

def crawl_site(start_url: str):
    """
    Crawls an entire website starting from a given URL.

    Args:
        start_url: The URL to begin crawling from.
    """
    to_visit = {start_url}
    visited = set()
    all_text_content = []

    print("🚀 Starting website crawl...")
    while to_visit:
        current_url = to_visit.pop()
        if current_url in visited:
            continue

        print(f"Scraping: {current_url}")
        visited.add(current_url)

        text, new_links = scrape_page(current_url)

        if text:
            all_text_content.append(f"\n\n--- Content from {current_url} ---\n\n{text}")

        for link in new_links:
            if link not in visited:
                to_visit.add(link)

    # Combine all scraped text and save to a file
    with open("aven_data.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(all_text_content))

    print(f"\n✅ Crawl complete. Scraped {len(visited)} pages.")
    print("All data saved to aven_data.txt")


if __name__ == '__main__':
    # The starting point for the crawl
    starting_url = "https://www.aven.com/support"
    crawl_site(starting_url)