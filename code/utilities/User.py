from utilities.AzureCosmosDBClient import AzureCosmosDBClient


class User:

    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role

    def get_name(self):
        return self.name

    def get_role(self):
        return self.role

    @staticmethod
    def get_user(principal_id: str):
        client = AzureCosmosDBClient()
        user = list(client.get_user(principal_id))

        if len(user) == 1:
            name = user[0]["name"]
            role = user[0]["role"]

            return User(name, role)

        else:
            return None

    @staticmethod
    def set_user(principal_id: str, principal_name: str, role: str):
        client = AzureCosmosDBClient()
        client.put_user(principal_id, principal_name, role)
        
