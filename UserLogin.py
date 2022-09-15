class UserLogin:
    def __init__(self, user_id=None):
        self.id = user_id

    def is_active(self):
        return True

    def get_id(self):
        return self.id

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False
