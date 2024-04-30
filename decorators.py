from functools import wraps
from flask import request,jsonify,make_response
from settings import API_KEY
import logging
# Decorator to add CORS headers to each response
def add_cors_headers(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        response = make_response(func(*args, **kwargs))
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, DELETE, HEAD, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        response.headers['Access-Control-Max-Age'] = '3600'  # Cache preflight response for 1 hour
        return response

    return decorated_function
def require_api_key(view_func):
    @wraps(view_func)
    def decorated(*args, **kwargs):
        # Assuming the request data is JSON
        api_key = request.args.get('api_key')

        if api_key == None:
            request_data = request.get_json()
            # Check if 'api_key' exists in the request data
            api_key = request_data.get('api_key')

        if api_key is None or api_key != API_KEY:
            logging.warning('{"Message": "Invalid API Key"}')
            return jsonify({"Message": "Invalid API Key"})


        return view_func(*args, **kwargs)

    return decorated

def require_password(view_func):
    '''
    Check for password in request
    '''
    @wraps(view_func)
    def decorated(*args, **kwargs):
        if request.method in ['POST','DELETE','OPTION','PUT'] and request.is_json:
        # Assuming the request data is JSON
            data = request.get_json()

            try:
                password:str = data['password']
                if password == None or password == r"":
                    raise ValueError
                else: 
                    return view_func(*args, **kwargs)
                    
            except KeyError:
                logging.error('{"Message":"Password required"} ,401')
                return jsonify({"Message":"Password required"}) ,401
            except ValueError:
                logging.error('{"Message":"Password cannot be empty"} ,401')
                return jsonify({"Message":"Password cannot be empty"}) ,401
            except Exception as e:
                logging.error(e)
                logging.error('{"Message":"Server Error"} ,500')
                return jsonify({"Message":"Server Error"}) ,500
        else:
            return view_func(*args, **kwargs)

            
    return decorated

