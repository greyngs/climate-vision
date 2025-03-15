import ee
import json
import os

def initialize_gee():
    try:
        ee.Image(0)
        return True
    except:
        pass
    
    try:
        if 'EE_SERVICE_ACCOUNT_JSON' in os.environ:            
            service_account_info = json.loads(os.environ['EE_SERVICE_ACCOUNT_JSON'])
            credentials = ee.ServiceAccountCredentials(
                service_account_info['client_email'],
                key_data=service_account_info['private_key']
            )            
            ee.Initialize(credentials, project='climate-change-vision')
            return True
    except Exception as e:
        print(f"Error starting with environment variables: {e}")
        return False
