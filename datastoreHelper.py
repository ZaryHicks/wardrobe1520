from google.cloud import datastore

# must import the relevant objects
import dataClasses

# this is a helper class that main.py uses to handle calls to the datastore

# gets the datastore client object
def get_client():
	return datastore.Client()


# logs msg (print) for debugging
def log(msg):
	print('datastore: %s' % msg)


# writes this User and password hash to the datastore
def save_user(user, passwordhash):
	# get datastore client
	client = get_client()
	
	# create entity - needs a datastore key, which we get from load_key
	# pass in client, kind, id
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
	q = client.query(kind='User')
	q.add_filter('username', '=', username)
	q.add_filter('passwordhash', '=', passwordhash)
	
	#call the query fetch and return User object if we find the user in datastore
	for user in q.fetch():
		return dataClasses.User(user['username'], user['firstname'], user['email'])
	return None


# loads datastore key using given client, kind, and id if provided
def load_key(client, kind, entity_id=None, parent_key=None):
	#if we do not pass in an id, it is none, else it is what we set is as
	# id is the "name" (string or int) can be auto generated as an int if not given
	# the key is the identifier, which is made of a kind and a name(id)
	
	key = None
	if entity_id: #if we are given an id, create key with it
		key = client.key(kind, entity_id, parent=parent_key)
	else: # if we are not given an id, we will let datastore generate an int for us
		key = client.key(kind)
	return key
