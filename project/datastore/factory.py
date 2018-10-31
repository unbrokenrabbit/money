import datastore.mongodb.manager

def get_datastore():
    return datastore.mongodb.manager.MongoManager()
