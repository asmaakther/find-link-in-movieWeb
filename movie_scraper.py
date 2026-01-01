name: Manual Scrape

on:
  workflow_dispatch:

jobs:
  scrape:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run scraper
        run: python movie_scraper.py   # <-- নাম ঠিক করতে হবে

      - name: Upload results
        uses: actions/upload-artifact@v4
        with:
          name: scrape-results
          path: stream_data.json
          if-no-files-found: warn
