# =======================================================
# বাংলা মন্তব্যসহ — m3u8 + mp4 Token + Cookie + Referrer সমর্থিত
# =======================================================

import json
import time
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import requests


# যেই পেজ থেকে ভিডিও ধরতে চাও
TARGET_URL = "https://www.watch-movies.com.pk/deva-2024-hindi-movie-watch-online-free/"


def start_driver():
    """হেডলেস ক্রোম ব্রাউজার চালু করা"""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(
        service=service,
        options=options
    )
    return driver


def get_stream_info():
    """নেটওয়ার্ক ট্রাফিক থেকে ভিডিও লিংক বের করা"""

    driver = start_driver()

    print("🌐 ওয়েবসাইট ওপেন করা হচ্ছে...")
    driver.get(TARGET_URL)

    print("⏳ ভিডিও প্লেয়ার লোডের জন্য অপেক্ষা...")
    time.sleep(25)

    print("🔍 নেটওয়ার্ক ট্রাফিক স্ক্যান করা হচ্ছে...")

    stream_url = None
    headers = {}

    for req in driver.requests:
        if req.response:

            url = req.url

            # m3u8 এবং mp4 — দুইটাই সাপোর্ট
            if any(x in url for x in [".m3u8", ".mp4"]):

                # বিজ্ঞাপন / গুগল বাদ
                if "ads" in url.lower() or "google" in url.lower():
                    continue

                stream_url = url
                headers = dict(req.headers)
                break

    if not stream_url:
        print("❌ কোনো ভিডিও লিংক পাওয়া যায়নি")
        driver.quit()
        return None, None, None

    print(f"\n✔ পাওয়া গেছে ভিডিও লিংক:\n{stream_url}\n")

    # কুকি সংগ্রহ
    cookies = driver.get_cookies()

    driver.quit()

    return stream_url, headers, cookies


def convert_cookies(cookie_list):
    """requests module-এর জন্য Cookie কনভার্ট"""
    cookie_dict = {}
    for c in cookie_list:
        cookie_dict[c["name"]] = c["value"]
    return cookie_dict


def test_request(url, headers, cookies):
    """Referrer + Cookie + UA সহ Request করা"""

    headers["Referer"] = TARGET_URL
    headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

    cookie_dict = convert_cookies(cookies)

    print("📡 একই ব্রাউজারের মতো রিকোয়েস্ট পাঠানো হচ্ছে...")

    r = requests.get(url, headers=headers, cookies=cookie_dict)

    print("HTTP Status:", r.status_code)

    if url.endswith(".m3u8") and "#EXTM3U" in r.text[:20]:
        print("🎬 এটি একটি বৈধ HLS Playlist")
    elif url.endswith(".mp4"):
        print("🎥 এটি একটি সরাসরি MP4 ফাইল")
    else:
        print("ℹ কনটেন্ট লোড হয়েছে")

    return r.text


if __name__ == "__main__":

    stream_url, headers, cookies = get_stream_info()

    if not stream_url:
        quit()

    playlist_content = test_request(stream_url, headers, cookies)

    data = {
        "source_page": TARGET_URL,
        "stream_url": stream_url,
        "headers_used": headers,
        "cookies_used": cookies,
    }

    # JSON ফাইল save
    with open("stream_data.json", "w") as f:
        json.dump(data, f, indent=4)

    print("\n💾 stream_data.json ফাইলে সব তথ্য সেভ হয়েছে")
