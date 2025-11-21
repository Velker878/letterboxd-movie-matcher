from letterboxd_scraper.utils import validate_usernames, scrape_watchlist, BASE_URL

# 1. Test username validation
valid, invalid = validate_usernames(["sahalwatches", "charliebrunet", "invaliduser123"])
print("VALID:", valid)
print("INVALID:", invalid)

# 2. Test scraping
url = BASE_URL + "/sahalwatches/watchlist/"
data = scrape_watchlist(url)

print("Films scraped:", len(data["id"]))
print(data["title"][:10])  # first 10 titles

#python -m letterboxd_scraper.debug_scraper