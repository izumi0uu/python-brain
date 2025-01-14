import requests
from requests.auth import HTTPBasicAuth
import json
from os.path import expanduser, join, dirname

def get_credentials():
    try:
        account_path = join(dirname(dirname(__file__)), 'account.txt')
        
        with open(account_path) as f:
            credentials = json.load(f)
            
        if not isinstance(credentials, list) or len(credentials) != 2:
            raise ValueError("Invalid credentials format in account.txt")
            
        return credentials[0], credentials[1]  # username, password
        
    except Exception as e:
        print(f"Error reading credentials: {e}")
        raise


def get_session(username=None, password=None):
    if username is None or password is None:
        username, password = get_credentials()
        
    def authenticate():
        session = requests.Session()
        session.auth = HTTPBasicAuth(username, password)  # 设置认证信息
        response = session.post("https://api.worldquantbrain.com/authentication")
        
        if response.status_code != 201:
            raise Exception(f"Authentication failed with status code: {response.status_code}")
        return session

    session = authenticate()
    
    # 包装所有HTTP方法
    original_get = session.get
    original_post = session.post
    original_put = session.put
    original_delete = session.delete
    
    def request_with_retry(method, *args, **kwargs):
        """统一的请求重试处理"""
        response = method(*args, **kwargs)
        if response.status_code == 401:
            nonlocal session
            session = authenticate()
            # 根据原始方法重新发送请求
            if method == original_get:
                response = session.get(*args, **kwargs)
            elif method == original_post:
                response = session.post(*args, **kwargs)
            elif method == original_put:
                response = session.put(*args, **kwargs)
            elif method == original_delete:
                response = session.delete(*args, **kwargs)
        return response
    
    # 替换所有HTTP方法
    session.get = lambda *args, **kwargs: request_with_retry(original_get, *args, **kwargs)
    session.post = lambda *args, **kwargs: request_with_retry(original_post, *args, **kwargs)
    session.put = lambda *args, **kwargs: request_with_retry(original_put, *args, **kwargs)
    session.delete = lambda *args, **kwargs: request_with_retry(original_delete, *args, **kwargs)
    
    return session
# if __name__ == "__main__":
#     try:
#         # 自动从account.txt读取凭据
#         session = get_session()
#         print("Login successful")
#     except Exception as e:
#         print(f"Login failed: {e}")