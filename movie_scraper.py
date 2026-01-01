import json
import time
import requests
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# -----------------------------
# ওয়েবসাইট লিস্ট
websites = [
    "https://www.watch-movies.com.pk",
    "https://www.movi.pk",
    "https://moviebox.ph",
    "https://playdesi.info",
    "https://en.fmovies24-to.com",
    "https://111.90.159.132",
    "https://ww25.soap2day.day"
]

# মুভি নাম লিস্ট
movies = [
    "russhabha (2025)",
    "Deva (2025)",
    "Talaash (2025)",
    "Red Sonja (2025)",
    "The Gorge (2025)",
    "The Accountant 2",
    "Moana 2"
]

# -----------------------------
def start_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# -----------------------------
def convert_cookies(cookie_list):
    cookie_dict = {}
    for c in cookie_list:
        cookie_dict[c["name"]] = c["value"]
    return cookie_dict

# -----------------------------
def scrape_movie(movie_name, website):
    """একটি ওয়েবসাইট থেকে মুভি ভিডিও লিংক খোঁজা"""
    driver = start_driver()
    results = []

    try:
        # ওয়েবসাইট + মুভি নাম URL build (simple search)
        url = f"{website}/{movie_name.replace(' ', '-').lower()}"
        print(f"🌐 Browsing: {url}")
        driver.set_page_load_timeout(60)
        driver.get(url)

        # স্ক্রল করে lazy load elements
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(30)  # অপেক্ষা করা প্লেয়ার লোডের জন্য

        # নেটওয়ার্ক ট্রাফিক চেক
        for req in driver.requests:
            if req.response:
                link = req.url
                if any(x in link for x in [".m3u8", ".mp4"]):
                    if "ads" not in link.lower() and "google" not in link.lower():
                        headers = dict(req.headers)
                        cookies = convert_cookies(driver.get_cookies())
                        results.append({
                            "stream_url": link,
                            "headers": headers,
                            "cookies": cookies,
                            "referrer": url
                        })
    except Exception as e:
        print(f"❌ Error for {movie_name} on {website}: {e}")
    finally:
        driver.quit()

    return results

# -----------------------------
def main():
    all_data = {}
    for movie in movies:
        all_data[movie] = {}
        for site in websites:
            links = scrape_movie(movie, site)
            all_data[movie][site] = links

    # সব ডেটা JSON ফাইলে save
    with open("stream_data.json", "w") as f:
        json.dump(all_data, f, indent=4)
    print("\n💾 stream_data.json ফাইলে সব তথ্য সেভ হয়েছে")

if __name__ == "__main__":
    main()
