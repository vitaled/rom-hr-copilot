from utilities.User import User
from streamlit.web.server.websocket_headers import _get_websocket_headers

class SessionHelper:

    @staticmethod
    def get_current_user():
        headers = _get_websocket_headers()

        principal_name = headers.get('x-ms-client-principal-name','dvitale@microsoft.com')
        principal_id = headers.get('x-ms-client-principal-id','cff054a1-bb8a-4e05-9218-9f3846d14ad8')
        
        user = User.get_user(principal_id)

        if user is None:
            user = User(principal_id    , principal_name,'None')
            User.set_user(principal_id, principal_name, 'None')
            
        return user