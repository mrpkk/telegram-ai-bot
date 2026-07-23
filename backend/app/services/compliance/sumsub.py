import requests
from app.core.config import SUMSUB_API_URL, SUMSUB_API_KEY

class SumsubClient:
    def __init__(self):
        self.base_url = SUMSUB_API_URL
        self.headers = {
            "X-App-Token": SUMSUB_API_KEY,
            "Content-Type": "application/json"
        }

    async def create_applicant(self, user_id: str, level_name: str = "basic-kyc-level") -> str:
        endpoint = f"{self.base_url}/resources/applicants"
        payload = {
            "externalUserId": user_id,
            "levelName": level_name
        }
        response = requests.post(endpoint, json=payload, headers=self.headers)
        return response.json()["id"]

    async def get_status(self, applicant_id: str) -> str:
        endpoint = f"{self.base_url}/resources/applicants/{applicant_id}/status"
        response = requests.get(endpoint, headers=self.headers)
        return response.json()["reviewStatus"]