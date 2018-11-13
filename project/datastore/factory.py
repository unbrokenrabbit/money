#import datastore.mysql.manager
import datastore.mongodb.manager

def get_datastore( _database_server ):
    return datastore.mongodb.manager.MongoManager()
    #return datastore.mysql.manager.MysqlManager( _database_server )
