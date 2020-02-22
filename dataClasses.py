# User object. Has a username, name, and email
class User(object):
    def __init__(self, username, firstname, email):
        self.username = username
		self.firstname = firstname
        self.email = email

    def to_dict(self):
        return {
            'username': self.username,
			'firstname': self.firstname
            'email': self.email,
        }