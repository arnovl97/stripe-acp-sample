"""
Agentic Commerce Protocol Client

Handles communication with the seller backend following ACP specification.
Provides methods for managing products, checkout sessions, and payment processing.
"""

import requests
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
import os
import stripe
from dotenv import load_dotenv


load_dotenv()

# ============================================================================
# CONSTANTS
# ============================================================================

SELLER_BACKEND_URL: str = os.getenv('SELLER_BACKEND_URL', 'http://localhost:3000')
API_VERSION: str = '2025-09-29'
CONTENT_TYPE_JSON: str = 'application/json'
FACILITATOR_TOKEN: str = 'Bearer facilitator_token'
DEFAULT_PAYMENT_PROVIDER: str = 'stripe'
SPT_EXPIRATION_DAYS: int = 1


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _calculate_expiration_timestamp(days_ahead: int) -> int:
    """
    Calculate Unix timestamp for a date in the future.
    
    Args:
        days_ahead: Number of days from now
        
    Returns:
        Unix timestamp as integer
    """
    expiration_date = datetime.now() + timedelta(days=days_ahead)
    return int(expiration_date.timestamp())


def _extract_total_amount_from_checkout(checkout_response: Dict[str, Any]) -> int:
    """
    Extract the total amount from a checkout response.
    
    Args:
        checkout_response: Response dictionary from get_checkout
        
    Returns:
        Total amount as integer
        
    Raises:
        ValueError: If total amount not found in checkout response
    """
    totals = checkout_response.get('totals', [])
    
    for total_entry in totals:
        if total_entry.get('type') == 'total':
            return total_entry['amount']
    
    raise ValueError('Total amount not found in checkout response')


# ============================================================================
# ACP CLIENT CLASS
# ============================================================================

class ACPClient:
    """
    Client for interacting with ACP-compliant seller backend.
    
    Handles HTTP communication with the seller backend API, including
    product listing, checkout session management, and payment processing.
    """
    
    def __init__(self, base_url: str = SELLER_BACKEND_URL) -> None:
        """
        Initialize ACP client with seller backend URL.
        
        Args:
            base_url: Base URL of the seller backend (defaults to config value)
        """
        self.base_url = base_url.rstrip('/')
        self.stripe = stripe
        self.stripe.api_key = os.environ["FACILITATOR_API_KEY"]

    
    def _build_headers(self) -> Dict[str, str]:
        """
        Build HTTP headers required for ACP API requests.
        
        Returns:
            Dictionary containing required headers
        """
        return {
            'Content-Type': CONTENT_TYPE_JSON,
            'Authorization': FACILITATOR_TOKEN,
            'API-Version': API_VERSION
        }
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to seller backend.
        
        Args:
            method: HTTP method (GET, POST, PUT)
            endpoint: API endpoint path
            data: Optional request body data
            
        Returns:
            JSON response as dictionary, or error dictionary if request fails
            
        Raises:
            ValueError: If unsupported HTTP method is used
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._build_headers()
        
        # Step 1: Validate HTTP method
        if method not in ['GET', 'POST', 'PUT']:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        # Step 2: Execute HTTP request based on method
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            
            # Step 3: Raise exception for HTTP errors
            response.raise_for_status()
            
            # Step 4: Return JSON response
            return response.json()
        
        except requests.exceptions.RequestException as e:
            # Step 5: Convert HTTP exceptions to error dictionary format
            status_code = None
            if hasattr(e, 'response') and e.response is not None:
                status_code = e.response.status_code
            
            return {
                'error': str(e),
                'status_code': status_code
            }
    
    def list_products(self) -> Dict[str, Any]:
        """
        Get list of available products from seller backend.
        
        Returns:
            Dictionary containing products list
        """
        return self.stripe.Product.list(limit=3)
    
    def create_checkout(
        self,
        items: List[Dict[str, Any]],
        buyer: Optional[Dict[str, str]] = None,
        fulfillment_address: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new checkout session.
        
        Args:
            items: List of items with id and quantity
            buyer: Optional buyer information (first_name, last_name, email, phone_number)
            fulfillment_address: Optional shipping address
            
        Returns:
            Dictionary containing checkout session details
        """
        data: Dict[str, Any] = {'items': items}
        
        if buyer:
            data['buyer'] = buyer
        
        if fulfillment_address:
            data['fulfillment_address'] = fulfillment_address
        
        return self._make_request('POST', '/checkout_sessions', data)
    
    def get_checkout(self, checkout_id: str) -> Dict[str, Any]:
        """
        Retrieve an existing checkout session.
        
        Args:
            checkout_id: Unique identifier for the checkout session
            
        Returns:
            Dictionary containing checkout session details
        """
        return self._make_request('GET', f'/checkout_sessions/{checkout_id}')
    
    def update_checkout(
        self,
        checkout_id: str,
        items: Optional[List[Dict[str, Any]]] = None,
        buyer: Optional[Dict[str, str]] = None,
        fulfillment_address: Optional[Dict[str, str]] = None,
        fulfillment_option_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update an existing checkout session.
        
        Args:
            checkout_id: ID of the checkout to update
            items: Optional updated items list
            buyer: Optional updated buyer information
            fulfillment_address: Optional updated shipping address
            fulfillment_option_id: Optional selected fulfillment option
            
        Returns:
            Dictionary containing updated checkout session details
        """
        data: Dict[str, Any] = {}
        
        if items is not None:
            data['items'] = items
        
        if buyer:
            data['buyer'] = buyer
        
        if fulfillment_address:
            data['fulfillment_address'] = fulfillment_address
        
        if fulfillment_option_id:
            data['fulfillment_option_id'] = fulfillment_option_id
        
        return self._make_request('POST', f'/checkout_sessions/{checkout_id}', data)
    
    def complete_checkout(
        self,
        checkout_id: str,
        payment_token: str,
        payment_provider: str = DEFAULT_PAYMENT_PROVIDER,
        billing_address: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Complete a checkout with payment.
        
        Args:
            checkout_id: ID of the checkout to complete
            payment_token: Payment token from payment provider
            payment_provider: Payment provider name (default: stripe)
            billing_address: Optional billing address
            
        Returns:
            Dictionary containing completion result
            
        Raises:
            ValueError: If total amount cannot be extracted from checkout
        """
        # Step 1: Get checkout details to extract total amount
        checkout_response = self.get_checkout(checkout_id)
        total_amount = _extract_total_amount_from_checkout(checkout_response)
        
        # Step 2: Build payment data structure
        payment_data: Dict[str, Any] = {
            'token': payment_token,
            'provider': payment_provider
        }
        
        # Step 3: Exchange payment token for SPT token
        tomorrow = datetime.now() + timedelta(days=1)
        expires_at_timestamp = int(tomorrow.timestamp()) 
        
        # ============================================================
        # DEMO MODE: Mock Stripe SPT Server (for European demo)
        # ============================================================
        mock_spt_url = os.getenv('MOCK_STRIPE_SPT_URL', 'http://localhost:8001')
        print(f"🎭 DEMO MODE: Using mock Stripe SPT server: {mock_spt_url}/v1/shared_payment/issued_tokens")
        
        get_pst_token_response = requests.post(
            url=f"{mock_spt_url}/v1/shared_payment/issued_tokens", 
            data={
                "payment_method": payment_token,
                "usage_limits[currency]": "usd",
                "usage_limits[max_amount]": total_amount,
                "usage_limits[expires_at]": expires_at_timestamp,
                "seller_details[network_id]": "internal",
                "seller_details[external_id]": "stripe_test_merchant",
            }
        )
        
        # # ============================================================
        # # PRODUCTION MODE: Real Stripe API (commented out)
        # # ============================================================
        # # Uncomment below and comment out DEMO MODE block above for production
        # #
        # # stripe_api_url = "https://api.stripe.com/v1/shared_payment/issued_tokens"
        # # print(f"💳 PRODUCTION MODE: Using real Stripe API: {stripe_api_url}")
        # # 
        # # get_pst_token_response = requests.post(
        # #     url=stripe_api_url, 
        # #     data={
        # #         "payment_method": payment_token,
        # #         "usage_limits[currency]": "usd",
        # #         "usage_limits[max_amount]": total_amount,
        # #         "usage_limits[expires_at]": expires_at_timestamp,
        # #         "seller_details[network_id]": "internal",
        # #         "seller_details[external_id]": "stripe_test_merchant",
        # #     },
        # #     auth=(os.getenv("FACILITATOR_API_KEY"), "")
        # # )
        
        print(get_pst_token_response.json())
        spt_token_id = get_pst_token_response.json()['id']
        
        payment_data['token'] = spt_token_id
        
        # Step 4: Build request data
        data: Dict[str, Any] = {'payment_data': payment_data}
        
        if billing_address:
            data['billing_address'] = billing_address
        
        # Step 5: Send completion request
        return self._make_request('POST', f'/checkout_sessions/{checkout_id}/complete', data)
    
    def cancel_checkout(self, checkout_id: str) -> Dict[str, Any]:
        """
        Cancel an existing checkout session.
        
        Args:
            checkout_id: ID of the checkout session to cancel
            
        Returns:
            Dictionary containing cancellation result
        """
        return self._make_request('POST', f'/checkout_sessions/{checkout_id}/cancel', {})
  