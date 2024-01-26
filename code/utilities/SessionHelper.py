from utilities.User import User
from streamlit.web.server.websocket_headers import _get_websocket_headers

DEFAULT_ROLE = 'User'

class SessionHelper:

    @staticmethod
    def get_current_user():
        headers = _get_websocket_headers()
        print(headers)
        principal_name = headers.get(
            'X-Ms-Client-Principal-Name', 'dvitale@microsoft.com')
        principal_id = headers.get(
            'X-Ms-Client-Principal-Id', 'cff054a1-bb8a-4e05-9218-9f3846d14ad8')

        user = User.get_user(principal_id)

        if user is None:
            user = User(principal_id, principal_name, DEFAULT_ROLE, [])
            User.set_user(principal_id, principal_name, DEFAULT_ROLE, [])

        return user
