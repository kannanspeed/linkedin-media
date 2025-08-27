import requests
import json
from datetime import datetime, timedelta
from urllib.parse import urlencode
import base64
import os

class LinkedInAPI:
    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.base_url = 'https://api.linkedin.com/v2'
        self.auth_url = 'https://www.linkedin.com/oauth/v2/authorization'
        self.token_url = 'https://www.linkedin.com/oauth/v2/accessToken'
    
    def get_authorization_url(self, state=None):
        """Generate LinkedIn OAuth authorization URL"""
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'openid profile email w_member_social',
            'state': state or 'random_state_string'
        }
        return f"{self.auth_url}?{urlencode(params)}"
    
    def get_access_token(self, authorization_code):
        """Exchange authorization code for access token"""
        data = {
            'grant_type': 'authorization_code',
            'code': authorization_code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            response = requests.post(self.token_url, data=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting access token: {e}")
            return None
    
    def get_user_profile(self, access_token):
        """Get user profile information using OpenID Connect"""
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            # Get user profile using OpenID Connect endpoint
            profile_response = requests.get(
                f"{self.base_url}/userinfo",
                headers=headers
            )
            profile_response.raise_for_status()
            profile_data = profile_response.json()
            
            # Extract profile picture URL if available
            profile_picture = profile_data.get('picture')
            
            return {
                'id': profile_data.get('sub'),  # OpenID Connect uses 'sub' for user ID
                'name': f"{profile_data.get('given_name', '')} {profile_data.get('family_name', '')}".strip(),
                'email': profile_data.get('email'),
                'profile_picture': profile_picture
            }
        except requests.exceptions.RequestException as e:
            print(f"Error getting user profile: {e}")
            return None
    
    def upload_image(self, access_token, image_path, user_id):
        """Upload image to LinkedIn"""
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            # Step 1: Register upload
            register_data = {
                "registerUploadRequest": {
                    "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                    "owner": f"urn:li:person:{user_id}",
                    "serviceRelationships": [{
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }]
                }
            }
            
            register_response = requests.post(
                f"{self.base_url}/assets?action=registerUpload",
                headers=headers,
                data=json.dumps(register_data)
            )
            register_response.raise_for_status()
            register_result = register_response.json()
            
            # Step 2: Upload the image
            upload_url = register_result['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
            asset_id = register_result['value']['asset']
            
            with open(image_path, 'rb') as image_file:
                upload_response = requests.put(upload_url, data=image_file)
                upload_response.raise_for_status()
            
            return asset_id
        except requests.exceptions.RequestException as e:
            print(f"Error uploading image: {e}")
            return None
        except Exception as e:
            print(f"Error processing image upload: {e}")
            return None
    
    def create_post(self, access_token, user_id, content, image_asset_id=None):
        """Create a LinkedIn post"""
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # For OpenID Connect, user_id is already the LinkedIn ID
        post_data = {
            "author": f"urn:li:person:{user_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": content
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        # Add image if provided
        if image_asset_id:
            post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "IMAGE"
            post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [{
                "status": "READY",
                "description": {
                    "text": "Image"
                },
                "media": image_asset_id,
                "title": {
                    "text": "Image"
                }
            }]
        
        try:
            response = requests.post(
                f"{self.base_url}/ugcPosts",
                headers=headers,
                data=json.dumps(post_data)
            )
            response.raise_for_status()
            result = response.json()
            return result.get('id')
        except requests.exceptions.RequestException as e:
            print(f"Error creating post: {e}")
            print(f"Response: {e.response.text if hasattr(e, 'response') else 'No response'}")
            return None
    
    def get_post_stats(self, access_token, post_id):
        """Get statistics for a specific post"""
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/socialActions/{post_id}",
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting post stats: {e}")
            return None
