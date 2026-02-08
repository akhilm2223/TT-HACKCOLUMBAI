import os
import requests
import json
from datetime import datetime

class FlowGladClient:
    """
    Client for FlowGlad API interactions.
    Handles Customer creation, Checkout Sessions, and Subscription status.
    """
    
    BASE_URL = "https://api.flowglad.com"

    def __init__(self):
        self.api_key = os.getenv("FLOWGLAD_API_KEY")
        if not self.api_key:
            print("Warning: FLOWGLAD_API_KEY not found in environment variables.")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def _handle_response(self, response):
        """Helper to handle API responses and errors."""
        try:
            if response.status_code in [200, 201]:
                return response.json()
            else:
                print(f"FlowGlad API Error {response.status_code}: {response.text}")
                return {"error": response.text, "status": response.status_code}
        except Exception as e:
            print(f"Error parsing response: {e}")
            return {"error": str(e)}

    def get_customer(self, org_id):
        """
        Fetch a customer by their external ID (Organization ID).
        Note: FlowGlad might not have a direct 'get by external id' endpoint easily accessible 
        without listing, so we might need to rely on creating/updating or listing with filter.
        
        However, for direct integration, we often use the 'create' endpoint which usually 
        returns the existing customer if they already exist (idempotency), or we list with filter.
        
        Let's try listing customers filtered by externalId if supported, or just return None
        and let the app handle creation.
        """
        # FlowGlad API structure might vary, but typically:
        # GET /customers?externalId=...
        try:
            url = f"{self.BASE_URL}/customers?search={org_id}" # optimizing for search
            response = requests.get(url, headers=self.headers)
            data = self._handle_response(response)
            
            if 'data' in data and len(data['data']) > 0:
                # Filter client-side if needed to be sure
                for customer in data['data']:
                    if customer.get('externalId') == org_id:
                        return customer
            return None
        except Exception as e:
            print(f"Failed to get customer: {e}")
            return None

    def create_customer(self, org_id, name, email):
        """
        Create a new customer in FlowGlad.
        """
        url = f"{self.BASE_URL}/customers"
        payload = {
            "externalId": org_id,
            "name": name,
            "email": email
            # Add other fields as necessary
        }
        
        response = requests.post(url, json=payload, headers=self.headers)
        return self._handle_response(response)

    def create_checkout_session(self, customer_id, price_id, success_url, cancel_url):
        """
        Create a checkout session for a subscription.
        """
        url = f"{self.BASE_URL}/checkout-sessions"
        payload = {
            "customerId": customer_id,
            "priceId": price_id,
            "successUrl": success_url,
            "cancelUrl": cancel_url,
            "mode": "subscription"
        }
        
        response = requests.post(url, json=payload, headers=self.headers)
        return self._handle_response(response)

    def get_subscription_status(self, customer_id):
        """
        Get the active subscription for a customer.
        Returns the subscription object if active, else None.
        """
        try:
            # Assuming endpoint /customers/{id}/subscriptions or similar
            # Or /subscriptions?customerId={id}
            url = f"{self.BASE_URL}/subscriptions?customerId={customer_id}"
            response = requests.get(url, headers=self.headers)
            data = self._handle_response(response)
            
            if 'data' in data:
                for sub in data['data']:
                    if sub.get('status') == 'active':
                        return sub
            return None
        except Exception as e:
            print(f"Failed to check subscription: {e}")
            return None

    def get_portal_url(self, customer_id):
        """
        Get the billing portal URL for a customer.
        Usually part of the customer object or a specific endpoint.
        """
        # Often returned in the customer object as 'billingPortalUrl'
        # If not, we might need to create a session.
        # Based on research, it's often a property.
        # We will try to fetch the customer again to get the latest URL.
        
        try:
            url = f"{self.BASE_URL}/customers/{customer_id}"
            response = requests.get(url, headers=self.headers)
            data = self._handle_response(response)
            if 'billingPortalUrl' in data:
                return data['billingPortalUrl']
            return None
        except Exception as e:
            print(f"Failed to get portal URL: {e}")
            return None
