from google.cloud import datastore
import json

# must import the relevant objects
import dataClasses

# this is a helper class that main.py uses to handle calls to the datastore

# gets the datastore client object
def get_client():
    return datastore.Client()


# logs msg (print) for debugging
def log(msg):
    print('datastore: %s' % msg)


# gets datastore key using given kind and chosen id if provided
def load_key(client, kind, entity_id=None, parent_key=None):
    key = None
    if entity_id:
        # if we are given an identifier, use it -- complete key
        key = client.key(kind, entity_id, parent=parent_key)
    else:
        # if we are not given an id, we will let datastore generate an int for us
        key = client.key(kind)
    return key


# writes this User and password hash to the datastore
def save_user(user, passwordhash):
    # get datastore client
    client = get_client()

    # create a new Entity of Kind "User"
    # Key will be ('User', username) -> So User key is identified by username
    entity = datastore.Entity(load_key(client, 'User', user.username))

    # key is set, now set entity values from the user object and passwordhash
    entity['username'] = user.username
    entity['firstname'] = user.firstname
    entity['email'] = user.email
    entity['passwordhash'] = passwordhash

    # save the entity to the datastore
    client.put(entity)


# check the datastore for a user with matching username and passhash (hashword)
def load_user(username, passwordhash):
    # get datastore client
    client = get_client()

    # create a datastore query for kind username, with username and passhash filters
    # we query to see if there is a User with the exact username and passhash provided
    q = client.query(kind='User')
    q.add_filter('username', '=', username)
    q.add_filter('passwordhash', '=', passwordhash)

    # call the query fetch and return User object if we find the user in datastore
    for user in q.fetch():
        return dataClasses.User(user['username'], user['firstname'], user['email'])
    return None


# Add item
def add_item(user, item):
    # get datastore client
    client = get_client()

    # idea is to use a transaction that either gets the entity or creates it if there is none
    with client.transaction():

        # new kind - Clothing
        # item key is Clothing/(random int id)
        # properties are: user(username), item_id(int for item type) and then the item itself(json string of the item)

        # key is based on Clothing kind, datastore will give us an int identifier
        key = client.key('Clothing')

        # Make a Clothing entity for this item
        clothing = datastore.Entity(key)

        # User who owns the item (for query)
        clothing['username'] = user
        # item type specified with an int id (for query)
        clothing['type'] = get_clothing_type(item.type)
        # the Clothing object itself
        clothing['data'] = json.dumps(item, indent=4, cls=dataClasses.ClothingEncoder)

        # from our entity, decode json in clothing property # into an array of clothing items # items = json.loads(wardrobe['clothing'])

        # put item into datastore
        client.put(clothing)


# Get clothing type - looks at type string and returns an int for the type
def get_clothing_type(type):
    if type == "Jacket":
        return 0
    elif type == "Shirt":
        return 1
    elif type == "Pants":
        return 2
    else:
        return 3


# get user's wardrobe info and return it to main as JSON
def get_wardrobe(user):
    # get datastore client
    client = get_client()

    # to get whole wardrobe, query all "Clothing" entities for the user's items
    # we will return an array of the Clothing items for this user

    q = client.query(kind='Clothing')
    q.add_filter('username', '=', user)

    items = []
    # for each Clothing kind fetched, add its data string to an array
    for item in q.fetch():
        # add each item into the array as a Clothing item loaded from the JSON
        items.append(json.loads(item['data']))

    # then we turn the entire array into JSON and send it to the client
    array_json = json.dumps(items, indent=4, cls=dataClasses.ClothingEncoder)
    return array_json


#deletes an item from the database
def delete_item(user,data):
    #get datastore client
    client = get_client()

    #creates a query based on the data
    q = client.query(kind='Clothing')
    q.add_filter('username', '=', user)

    for element in data:
        if 'id' in element:
            del element['id']
        if 'state' in element:
            del element['state']
        for item in q.fetch():
            if json.loads(item['data'])==element:
                client.delete(item.key)
        q = client.query(kind='Clothing')
        q.add_filter('username', '=', user)