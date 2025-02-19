from rest_framework_simplejwt.authentication import JWTAuthentication

class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            raw_token = request.GET.get('token') or request.POST.get('token')
            if raw_token:
                header = self.get_raw_token(raw_token)
        
        if header is None:
            print("No authentication header found")
            return None

        try:
            raw_token = self.get_raw_token(header)
            if raw_token is None:
                print("No raw token found")
                return None

            validated_token = self.get_validated_token(raw_token)
            print(f"Token validated successfully: {validated_token}")
            
            user = self.get_user(validated_token)
            print(f"User authenticated: {user.email}")
            
            return (user, validated_token)
        except Exception as e:
            print(f"Authentication error: {str(e)}")
            return None

    def get_raw_token(self, header):
        """
        Extracts token from header, being more lenient with the format
        """
        if isinstance(header, str):
            # Try different common formats
            if header.startswith('Bearer '):
                return header[7:]
            if header.startswith('JWT '):
                return header[4:]
            if header.startswith('Token '):
                return header[6:]
            # If no prefix, try to use the token as is
            return header
        return None
