from letterboxd_scraper.utils import scrape_watchlist

def test_scraper():
    print("Running scraper test...")

    url = "https://letterboxd.com/nathanvelker/watchlist/"  # Replace with a real username
    data = scrape_watchlist(url)

    print("Scraper returned keys:", list(data.keys()))
    print("Number of films scraped:", len(data["id"]))

    assert isinstance(data, dict)
    assert "title" in data

if __name__ == "__main__":
    test_scraper()
