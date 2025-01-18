from supabase import create_client, Client
from config import Config

class SupabaseAuthenticator:
    def __init__(self):
        self.client: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    
    def sign_up(self, email, password):
        response = self.client.auth.sign_up({
            "email": self.email,
            "password": self.password
        })
        return response
    
    def sign_in_with_password(self, email, password):
        response = self.client.auth.sign_in_with_password({
            "email": self.email,
            "password": self.password
        })
        # has access_token and refresh_token, store them in local storage
        self.sign_in_response = response
        return response
    
    def set_session(self, access_token: str, refresh_token: str):
        # Use the token to reauthenticate
        return self.client.auth.set_session(access_token, refresh_token)
    
    def get_user_id(self):
        try:
            response = self.client.auth.get_user()
            user_id = response.user.id
            return user_id
        except:
            return None
        
    def get_acceess_token(self):
        try:
            response = self.client.auth.get_session()
            access_token = response.access_token
            return access_token
        except:
            return None
        
    def get_client(self):
        return self.client