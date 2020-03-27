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

    # idea is to use a transaction that either gets the entity or creates it if need be?
    with client.transaction():
        # key is based on Wardrobe kind and id by username
        key = client.key('Wardrobe', user)

        # get the Wardrobe entity
        wardrobe = client.get(key)

        # need to use JSON probably
        # serialize our list of clothing into json, store that
        # when we read, read in the json into a list of clothing,
        # add to it, serialize back

        # if a Wardrobe does not exist for this user
        if not wardrobe:
            # create a Wardrobe entity with this key (username)
            wardrobe = datastore.Entity(key)

            # items is an array of clothing, containing our first item
            items = [item]
            # items.append(item)

            # serialize the array (here only one item) into json
            array_json = json.dumps(items, indent=4, cls=dataClasses.ClothingEncoder)

            # then set clothing property to this json string
            wardrobe['clothing'] = array_json
            # client.put(wardrobe)
        else:
            # else if the entity already exists, we add the item to the list

            # from our entity, decode json in clothing property
            # into an array of clothing items
            items = json.loads(wardrobe['clothing'])

            # append the item we are adding to the list
            items.append(item)

            array_json = json.dumps(items, indent=4, cls=dataClasses.ClothingEncoder)
            wardrobe['clothing'] = array_json

        client.put(wardrobe)

# get user's wardrobe info and return it to main as JSON
def get_wardrobe(user):
    # get datastore client
    client = get_client()

    # idea is to use a transaction that either gets the entity or creates it if need be?
    with client.transaction():
        # key is based on Wardrobe kind and id by username
        key = client.key('Wardrobe', user)

        # get the Wardrobe entity
        wardrobe = client.get(key)

        # from our entity, decode json in clothing property
        # into an array of clothing items
        items = json.loads(wardrobe['clothing'])

        array_json = json.dumps(items, indent=4, cls=dataClasses.ClothingEncoder)

    return array_json
