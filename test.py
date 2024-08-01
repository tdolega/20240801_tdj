import unittest
import requests


class ValidateEndpoint(unittest.TestCase):
    BASE_URL = "http://127.0.0.1:5000"
    ENDPOINT = "/endpoint"
    API_KEY = "rekrutacja2024"
    RATE_LIMIT = 3

    def test_valid_data(self):
        response = requests.post(
            self.BASE_URL + self.ENDPOINT,
            json=[
                {"num": 1, "text": "x"},
                {"num": 2.5, "text": ""},
                {"num": -1e-5, "text": "żółć"},
            ],
            headers={"apikey": self.API_KEY},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"valid": 3, "invalid": 0})

    def test_invalid_data_format(self):
        response = requests.post(
            self.BASE_URL + self.ENDPOINT,
            json="invalid data",
            headers={"apikey": self.API_KEY},
        )
        self.assertEqual(response.status_code, 400)

    def test_invalid_structure(self):
        response = requests.post(
            self.BASE_URL + self.ENDPOINT,
            json=[
                {"num": 1},
                {"text": "missing num"},
                {"num": "not a number", "text": "xyz"},
                {"num": 1, "text": 1},
                {"wrong_key": 1, "text": "xyz"},
            ],
            headers={"apikey": self.API_KEY},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"valid": 0, "invalid": 5})

    def test_rate_limit(self):
        for _ in range(self.RATE_LIMIT):
            response = requests.post(
                self.BASE_URL + self.ENDPOINT,
                json=[
                    {"num": 1, "text": "xyz"},
                ],
            )
        self.assertNotEqual(response.status_code, 429)
        response = requests.post(
            self.BASE_URL + self.ENDPOINT,
            json=[
                {"num": 1, "text": "xyz"},
            ],
        )
        self.assertEqual(response.status_code, 429)

    def test_rate_limit_with_api_key(self):
        for _ in range(self.RATE_LIMIT + 1):
            response = requests.post(
                self.BASE_URL + self.ENDPOINT,
                json=[
                    {"num": 1, "text": "xyz"},
                ],
                headers={"apikey": self.API_KEY},
            )
        self.assertNotEqual(response.status_code, 429)

    def test_empty_list(self):
        response = requests.post(
            self.BASE_URL + self.ENDPOINT,
            json=[],
            headers={"apikey": self.API_KEY},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"valid": 0, "invalid": 0})

    def test_invalid_method(self):
        response = requests.get(self.BASE_URL + self.ENDPOINT)
        self.assertEqual(response.status_code, 405)


if __name__ == "__main__":
    unittest.main()
