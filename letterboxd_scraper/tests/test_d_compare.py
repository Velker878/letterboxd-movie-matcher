import django
django.setup()

from letterboxd_scraper.services import compare_users

def test_compare_real_users():
    usernames = ["lilymoviee", "charliebrunet"]

    result = compare_users(usernames)

    print("Valid users:", result["valid_usernames"])
    print("Common films:", len(result["common_films"]))

    assert len(result["valid_usernames"]) == 2
    assert isinstance(result["common_films"], list)

if __name__ == "__main__":
    test_compare_real_users()


