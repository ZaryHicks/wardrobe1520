# User object. Has a username, name, and email
class User(object):
	def __init__(self, username, firstname, email):
		self.username = username
		self.firstname = firstname
		self.email = email

	def to_dict(self):
		return {
			'username': self.username,
			'firstname': self.firstname,
            'email': self.email,
        }

# Clothing object (WIP) - Do we have different subclasses? 
class Item(object):
    def __init__(self, name):
        self.name = name
    
    def to_dict(self):
        return {
            'name': self.name,
        }

# say our clothes options are: coat/jacket, top, bottom, shoes?

# Subclasses of Item?
#class jacket(item):
#class shirt(item):
#class pants(item):
#class shoes(item):