from letterboxd_scraper.utils import scrape_watchlist

# Test with a public profile (yours or a popular one)
test_url = "https://letterboxd.com/lilymoviee/watchlist/"
data = scrape_watchlist(test_url)

if data:
    print(f"✅ Scraper works! Found {len(data)} movies.")
    print(f"First movie: {data[0]['title']} ({data[0]['year']})")
else:
    print("❌ Scraper failed to find the list. Check the HTML selectors in utils.py.")