from django.test import TestCase, Client

class TestCompareEndpoint(TestCase):
    def test_compare_endpoint(self):
        client = Client()

        response = client.get("/compare/?usernames=lilymoviee&usernames=charliebrunet")

        print("Status code:", response.status_code)
        print("JSON response:", response.json())

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertIn("common_films", response.json())
        self.assertIsInstance(response.json()["common_films"], list)