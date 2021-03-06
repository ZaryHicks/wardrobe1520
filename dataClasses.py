import json
from json import JSONEncoder

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


# Potential setup for the clothing classes.
class Clothing(object):
    def __init__(self, type, name, color, is_casual, high_temp, low_temp, tags):
        self.type = type
        self.name = name
        self.color = color
        self.is_casual = is_casual
        self.high_temp = high_temp
        self.low_temp = low_temp
        self.tags = tags

    def to_dict(self):
        return {
            'type': self.type,
            'name': self.name,
            'color': self.color,
            'is_casual': self.is_casual,
            'high_temp': self.high_temp,
            'low_temp': self.low_temp,
            'tags': self.tags,
        }

    def check_temp(self, temp):
        if (self.high_temp >= temp and temp >= self.low_temp):
            return True
        else:
            return False


#subclass of JSONEncoder to serialize Clothing
class ClothingEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


class Jacket(Clothing):
    def __init__(self, name, color, is_casual, high_temp, low_temp):
        super().__init__(name, color, is_casual, high_temp, low_temp)


class Shirt(Clothing):
    def __init__(self, name, color, is_casual, high_temp, low_temp, is_long):
        super().__init__(name, color, is_casual, high_temp, low_temp)
        self.is_long = is_long

    def to_dict(self):
        return {
            'name': self.name,
            'color': self.name,
            'is_casual': self.name,
            'high_temp': self.name,
            'low_temp': self.name,
            'is_long': self.is_long
        }


class Pants(Clothing):
    def __init__(self, name, color, is_casual, high_temp, low_temp, is_long):
        super().__init__(name, color, is_casual, high_temp, low_temp)
        self.is_long = is_long

    def to_dict(self):
        return {
            'name': self.name,
            'color': self.name,
            'is_casual': self.name,
            'high_temp': self.name,
            'low_temp': self.name,
            'is_long': self.is_long
        }


class Shoes(Clothing):
    def __init__(self, name, color, is_casual, high_temp, low_temp):
        super().__init__(name, color, is_casual, high_temp, low_temp)
