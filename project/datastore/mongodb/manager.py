from pymongo import MongoClient
import pymongo
import datastore.transaction as trans
import datastore.bucket as datastore_bucket
import bson


#    def __init__( _self, _database_server ):
#    def get_bucket_id( _self, _bucket ):
#    def build_get_bucket_id_query( _self, _bucket ):
#    def is_bucket_present( _self, _bucket ):
#    def is_bucket_name_present( _self, _bucket_name ):
#    def insert_bucket( _self, _bucket_name_id, _bucket_rule_id ):
#    def insert_bucket_name( _self, _name ):
#    def insert_bucket_rule( _self, _pattern, _account, _direction ):
#    def remove_bucket( _self, _id ):
#    def get_bucket_name_id( _self, _bucket_name ):

class MongoManager:

    def get_database( _self ):
        mongo_client = MongoClient( 'money-mongodb' )

        return  mongo_client.money_db


    def initialize_database( _self ):
        db = _self.get_database()

        db.transactions.remove()
        db.buckets.remove()
        db.bucket_import_settings.remove()

        bucket_import_settings = {
                    'last_account': 'checking_spending',
                    'last_direction': 'income'
        }
        db.bucket_import_settings.insert_one( bucket_import_settings )


    def get_bucket_import_settings( _self ):
        db = _self.get_database()
        bucket_import_settings = db.bucket_import_settings.find_one()

        return bucket_import_settings


    def set_bucket_import_settings( _self, _last_account, _last_direction ):
        db = _self.get_database()

        update = {
            '$set': {
                'last_account': _last_account,
                'last_direction': _last_direction
            }
        }

        db.bucket_import_settings.update_one(
            {},
            update,
            upsert=True
        )


    def upsert_transactions( _self, _transactions ):
        db = _self.get_database()
    
        new_transaction_count = 0
        updated_transaction_count = 0
        for transaction in _transactions:
            document = {}
            document[ 'account' ] = transaction.account
            document[ 'date' ] = transaction.date
            document[ 'amount' ] = transaction.amount
            document[ 'description' ] = transaction.description
            document[ 'instance' ] = transaction.instance
            document[ 'bucket' ] = transaction.bucket
            document[ 'bucket_status' ] = transaction.bucket_status

            update_result = db.transactions.update(
                document,
                document,
                #{
                #    "$set": document,
                #},
                upsert = True
            )

            if( update_result[ 'updatedExisting' ] ):
                updated_transaction_count += 1
            else:
                new_transaction_count += 1

        result = {}
        result[ 'updated_transaction_count' ] = updated_transaction_count
        result[ 'new_transaction_count' ] = new_transaction_count
        
        return result

    def apply_bucket_to_transaction( _self, _transaction, _bucket, _bucket_state='unapproved' ):
        db = _self.get_database()
        
        where_clause = {
                'account': _transaction.account,
                'date': _transaction.date,
                'amount': _transaction.amount,
                'description': _transaction.description,
                'instance': _transaction.instance,
                'bucket': _transaction.bucket,
                'bucket_status': _transaction.bucket_status
        }

        update_clause = {
                '$set': {
                    'bucket': _bucket.name,
                    'bucket_status': _bucket_state
                }
        }
            
        results = db.transactions.update( where_clause, update_clause )


    def retrieve_transactions( _self ):
        db = _self.get_database()
        
        transactions = []
        results = db.transactions.find().sort( [ ( 'date', -1 ) ] )
        for result in results:
            transaction = trans.Transaction()
            transaction.from_dict( result )
            transactions.append( transaction )

        return transactions


    def get_unbucketed_transactions( _self ):
        db = _self.get_database()
        
        transactions = []

        where_clause = {
                "bucket": ""
        }
        results = db.transactions.find( where_clause )
        for result in results:
            transaction = trans.Transaction()
            transaction.from_dict( result )
            transactions.append( transaction )

        return transactions


    def get_unapproved_transactions( _self ):
        db = _self.get_database()
        
        transactions = []

        where_clause = {
                "bucket_status": "unapproved"
        }
        results = db.transactions.find( where_clause )
        for result in results:
            transaction = trans.Transaction()
            transaction.from_dict( result )
            transactions.append( transaction )

        return transactions       


    def remove_all_transactions( _self ):
        db = _self.get_database()
        result = db.transactions.remove()

        return result[ 'n' ]
        

    def add_bucket( _self, _bucket_name, _bucket_account, _bucket_direction, _bucket_pattern ):
        updated_bucket_count = 0
        new_bucket_count = 0

        db = _self.get_database()
        query = {
                'name': _bucket_name,
                'account': _bucket_account,
                'direction': _bucket_direction
        }
        #projection = {
        #        '_id': 0
        #}

        #document = db.buckets.find_one( query, projection )
        document = db.buckets.find_one( query )
        if( document ):
            if( _bucket_pattern not in document[ 'patterns' ] ):
                document[ 'patterns' ].append( _bucket_pattern )
        else:
            document = {
                    'name': _bucket_name,
                    'patterns': [
                            _bucket_pattern
                    ],
                    'account': _bucket_account,
                    'direction': _bucket_direction
            }

        update_filter = {
            'name': _bucket_name,
            'account': _bucket_account,
            'direction': _bucket_direction
        }

        update_result = db.buckets.update(
            update_filter,
            document,
            #{
            #    "$set": document,
            #},
            upsert = True
        )

        if( update_result[ 'updatedExisting' ] ):
            updated_bucket_count += 1
        else:
            new_bucket_count += 1

        result = {}
        result[ 'updated_bucket_count' ] = updated_bucket_count
        result[ 'new_bucket_count' ] = new_bucket_count
        
        return result

    #def remove_bucket( _self, _id ):
    #    db = _self.get_database()
    #    
    #    return db.buckets.remove( { "_id": bson.objectid.ObjectId( _id ) } )

    def get_buckets( _self ):
        db = _self.get_database()
        
        buckets = []
        results = db.buckets.find()
        for result in results:
            for pattern in result[ 'patterns' ]:
                bucket = datastore_bucket.Bucket(
                    #_id = result[ '_id' ],
                    _name = result[ 'name' ],
                    _pattern = pattern,
                    _account = result[ 'account' ],
                    _direction = result[ 'direction' ]
                )

                buckets.append( bucket )

        return buckets

    def get_accounts( _self ):
        # TODO implement
        return [
                'checking_spending',
                'checking_bills',
                'checking_savings',
                'credit_spending',
                'credit_bills'
        ]


    def match_buckets_to_transactions( _self ):
        db = _self.get_database()

        #self.stripTags()

        buckets = db.buckets.find()

        for bucket in buckets:
            for pattern in bucket[ 'patterns' ]:
                find_clause = {}
                find_clause[ 'description' ] = { '$regex': pattern }
                find_clause[ 'account' ] = bucket[ 'account' ]

                if( bucket[ 'direction' ] == 'income' ):
                    find_clause[ 'amount' ] = { '$gte': 0 }
                elif( bucket[ 'direction' ] == 'expense' ):
                    find_clause[ 'amount' ] = { '$lte': 0 }

                results = db.transactions.update(
                    find_clause,
                    {
                        "$set":
                        {
                            "bucket": bucket[ 'name' ]
                        }
                    },
                    multi=True
                )


