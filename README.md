# Letterboxd Watchlist Matcher Web App

Web app that compares Letterboxd watchlists between users and shows the movies they have in common

## Tech Stack

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python (Django)
- **Web Scraping:** BeautifulSoup (bs4), Requests
- **External API:** The Movie Database (TMDB)

## Project Status
**Stage:** Complete MVP

**What's in store:**
- Performance optimizations
- Nicer looking UI and better UX
- AI-powered recommendations
- Deployment

## Getting Started

1. Clone this repository:

   ```bash
   git clone https://github.com/Velker878/letterboxd-movie-matcher.git
   cd letterboxd-movie-matcher
   ```
2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate # Windows: venv\\Scripts\\activate
   ```
3. Install dependencies:
   
   ```bash
   pip install -r requirements.txt
   ```
5. Add your TMDB API key to Django settings or environment variables.
6. Run the development server:

   ```bash
   python manage.py runserver
   ```
## Notes & Limitations
- Letterboxd does not provide an official API — scraping relies on current HTML structure
- Some titles are unique to Letterboxd and do not appear on TMDB — results are sometimes not displayed
## License

This project is licensed under the [MIT License](LICENSE).
