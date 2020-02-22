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


"""
def create_data():
    """You can use this function to populate the datastore with some basic
    data."""

    client = _get_client()
    entity = datastore.Entity(client.key(_USER_ENTITY, 'testuser'),
                              exclude_from_indexes=[])
    entity.update({
        'username': 'testuser',
        'passwordhash': '',
        'email': '',
        'about': '',
        'completions': [],
    })
    client.put(entity)

    entity = datastore.Entity(client.key(_COURSE_ENTITY, 'Course01'),
                              exclude_from_indexes=['description', 'code'])
    entity.update({
        'code': 'Course01',
        'name': 'First Course',
        'description': 'This is a description for a test course.  In the \
future, real courses will have lots of other stuff here to see that will tell \
you more about their content.',
    })
    client.put(entity)
    entity = datastore.Entity(client.key(_COURSE_ENTITY, 'Course02'),
                              exclude_from_indexes=['description', 'code'])
    entity.update({
        'code': 'Course02',
        'name': 'Second Course',
        'description': 'This is also a course description, but maybe less \
wordy than the previous one.'
    })
    client.put(entity)
    entity = datastore.Entity(client.key(_COURSE_ENTITY,
                                         'Course01',
                                         _LESSON_ENTITY),
                              exclude_from_indexes=['content', 'title'])
    entity.update({
        'title': 'Lesson 1: The First One',
        'content': 'Imagine there were lots of video content and cool things.',
    })
    client.put(entity)
    entity = datastore.Entity(client.key(_COURSE_ENTITY,
                                         'Course01',
                                         _LESSON_ENTITY),
                              exclude_from_indexes=['content', 'title'])
    entity.update({
        'title': 'Lesson 2: Another One',
        'content': '1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11',
    })
    client.put(entity)
    entity = datastore.Entity(client.key(_COURSE_ENTITY,
                                         'Course02',
                                         _LESSON_ENTITY),
                              exclude_from_indexes=['content', 'title'])
    entity.update({
        'title': 'Lesson 1: The First One, a Second Time',
        'content': '<p>Things</p><p>Other Things</p><p>Still More Things</p>',
    })

    client.put(entity)
    entity = datastore.Entity(client.key(_COURSE_ENTITY,
                                         'Course02',
                                         _LESSON_ENTITY),
                              exclude_from_indexes=['content', 'title'])
    entity.update({
        'title': 'Lesson 2: Yes, Another One',
        'content': '<ul><li>a</li><li>b</li><li>c</li><li>d</li><li></ul>',
    })
    client.put(entity)
"""