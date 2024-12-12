import requests
from typing import Dict, List, Optional
import time

class APIClient:
    def __init__(self, base_url: str = "http://localhost:8000", max_retries: int = 3):
        self.base_url = base_url
        self.max_retries = max_retries
        self.session = requests.Session()

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        url = f"{self.base_url}{endpoint}"
        retries = 0
        last_error = None

        while retries < self.max_retries:
            try:
                response = self.session.request(method, url, **kwargs)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.ConnectionError as e:
                last_error = f"Could not connect to server: {str(e)}"
                retries += 1
                if retries < self.max_retries:
                    time.sleep(1)  # Așteptăm 1 secundă înainte de reîncercare
            except requests.exceptions.RequestException as e:
                raise Exception(f"API request failed: {str(e)}")

        raise Exception(last_error or "Maximum retries exceeded")

    def get_organizations(self) -> List[Dict]:
        return self._make_request("GET", "/organizations/")

    def get_organization(self, org_id: int) -> Dict:
        return self._make_request("GET", f"/organizations/{org_id}")

    def create_organization(self, data: Dict) -> Dict:
        return self._make_request("POST", "/organizations/", json=data)

    def update_organization(self, org_id: int, data: Dict) -> Dict:
        return self._make_request("PUT", f"/organizations/{org_id}", json=data)

    def delete_organization(self, org_id: int) -> None:
        self._make_request("DELETE", f"/organizations/{org_id}")

    def get_invoices(self) -> List[Dict]:
        try:
            response = self._make_request("GET", "/invoices/")
            return response
        except Exception as e:
            print(f"Error in get_invoices: {str(e)}")
            print(f"Response content: {getattr(e, 'response', {}).get('content', 'No content')}")
            raise

    def get_invoice(self, invoice_id: int) -> Dict:
        return self._make_request("GET", f"/invoices/{invoice_id}")

    def create_invoice(self, data: Dict) -> Dict:
        return self._make_request("POST", "/invoices/", json=data)

    def update_invoice(self, invoice_id: int, data: Dict) -> Dict:
        return self._make_request("PUT", f"/invoices/{invoice_id}", json=data)

    def delete_invoice(self, invoice_id: int) -> None:
        self._make_request("DELETE", f"/invoices/{invoice_id}")