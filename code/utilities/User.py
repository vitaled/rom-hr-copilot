from utilities.AzureCosmosDBClient import AzureCosmosDBClient


class User:

    def __init__(self, id: int, name: str, role: str, profiles: list):
        self.id = id
        self.name = name
        self.role = role
        self.profiles = profiles

    def get_name(self):
        return self.name

    def get_role(self):
        return self.role

    def get_profiles(self):
        return self.profiles

    @staticmethod
    def get_user(principal_id: str):
        client = AzureCosmosDBClient()
        user = list(client.get_user(principal_id))

        if len(user) == 1:
            name = user[0]["name"]
            role = user[0]["role"]
            profiles = user[0]["profiles"]

            return User(principal_id, name, role, profiles)

        else:
            return None

    @staticmethod
    def set_user(principal_id: str, principal_name: str, role: str, profiles: list):
        client = AzureCosmosDBClient()
        client.put_user(principal_id, principal_name, role, profiles)
