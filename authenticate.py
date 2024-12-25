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