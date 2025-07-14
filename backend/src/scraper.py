import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

def scrape_page_with_selenium(url: str) -> str | None:
    """
    Scrapes a single page that requires JavaScript, using Selenium.

    Args:
        url: The URL of the page to scrape.

    Returns:
        The cleaned text content of the page, or None if an error occurs.
    """
    print(f"Scraping: {url}")
    # Set up Chrome options for headless Browse
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # Initialize the Chrome driver automatically
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        driver.get(url)
        # Give the JavaScript time to load the content.
        # This value may need to be adjusted.
        time.sleep(3) 

        # Now that the page is loaded, get the HTML and parse it
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()

        text = soup.get_text(separator='\n', strip=True)
        return text

    except Exception as e:
        print(f"  -> Error scraping {url}: {e}")
        return None
    finally:
        # Important: Quit the driver to free up resources
        driver.quit()

def scrape_specific_pages(urls: list[str], output_file: str):
    """
    Scrapes a specific list of URLs and saves their combined text to a file.
    """
    all_text_content = []
    print("🚀 Starting targeted scrape with Selenium...")
    for url in urls:
        text = scrape_page_with_selenium(url)
        if text:
            all_text_content.append(f"\n\n--- Content from {url} ---\n\n{text}")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(all_text_content))

    print(f"\n✅ Scrape complete.")
    print(f"All data saved to {output_file}")


if __name__ == '__main__':
    target_urls = [
        "https://www.aven.com/about",
        "https://www.aven.com/education",
        "https://www.aven.com/support",
        "https://www.aven.com/app",
        "https://www.aven.com/contact"
    ]
    output_filename = "aven_data.txt"
    scrape_specific_pages(target_urls, output_filename)