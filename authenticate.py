from supabase import create_client, Client
from config import Config

class SupabaseAuthenticator:
    def __init__(self, email, password):
        self.client: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
        self.email: str = email
        self.password: str = password
    
    def sign_up(self):
        response = self.client.auth.sign_up({
            "email": self.email,
            "password": self.password
        })
        return response
    
    def sign_in_with_password(self):
        response = self.client.auth.sign_in_with_password({
            "email": self.email,
            "password": self.password
        })
        self.sign_in_response = response
        return response
    
    def get_user_id(self):
        if self.sign_in_response.get("data"):
            return self.sign_in_response["data"]["user"]["id"]
        else:
            print("Authentication failed:", self.sign_in_response)
            return None