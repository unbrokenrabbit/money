
from pymongo import MongoClient
import pymongo
import datastore.transaction as trans
import datastore.bucket as datastore_bucket
import bson


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
            query = {
                'account': transaction.account,
                'amount': transaction.amount,
                'date': transaction.date,
                'description': transaction.description,
                'instance': transaction.instance
            }

            update = {
                '$set': {
                    'account': transaction.account,
                    'amount': transaction.amount,
                    'date': transaction.date,
                    'description': transaction.description,
                    'instance': transaction.instance
                },
                '$setOnInsert': {
                    'bucket': '',
                    'bucket_status': 'unapproved'
                }
            }

            update_result = db.transactions.update(
                query,
                update,
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


    def retrieve_transactions( _self, _start_date=None, _end_date=None ):
        db = _self.get_database()
        
        sort_clause = [
            ( 'date', -1 )
        ]
        transactions = []
        if( ( _start_date is not None ) and ( _end_date is not None ) ):
            match_clause = {
                'date': {
                    '$lt': _end_date,
                    '$gte': _start_date
                }
            }
            results = db.transactions.find( match_clause ).sort( sort_clause )
        else:
            results = db.transactions.find().sort( sort_clause )

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


    def get_distinct_expenses( _self, _start_date, _end_date ):
        db = _self.get_database()

        matches_clause = {
            '$and':
            [
                { 'date': { '$gte': _start_date } },
                { 'date': { '$lt': _end_date } },
                { 'bucket': { '$regex': 'expense_.*' } }
            ]
        }
        group_clause = {
            '_id': '$bucket',
            'total': { '$sum': '$amount' }
        }
        #aggregation_results = db.test_transactions.aggregate(
        aggregation_results = db.transactions.aggregate(
            [
                { '$match': matches_clause },
                { '$group': group_clause },
                { '$sort': { 'total': 1 } }
            ]
        )
        aggregation_result_count = 0
        distinct_expenses = []
        for result in aggregation_results:
            aggregation_result_count += 1
            #distinct_expense = CategorizedTotal()
            #distinct_expense.tag = result[ '_id' ]
            #distinct_expense.total = result[ 'total' ]

            #distinct_expenses.append( distinct_expense )
            distinct_expense = {
                'name': result[ '_id' ],
                'total': ( result[ 'total' ] * -1 )
            }
            distinct_expenses.append( distinct_expense )
            #distinct_expenses.append( result )

        return distinct_expenses


    def get_distinct_incomes( _self, _start_date, _end_date ):
        db = _self.get_database()

        matches_clause = {
            '$and':
            [
                { 'date': { '$gte': _start_date } },
                { 'date': { '$lt': _end_date } },
                { 'bucket': { '$regex': 'income_.*' } }
            ]
        }
        group_clause = {
            '_id': '$bucket',
            'total': { '$sum': '$amount' }
        }
        #aggregation_results = db.test_transactions.aggregate(
        aggregation_results = db.transactions.aggregate(
            [
                { '$match': matches_clause },
                { '$group': group_clause },
                { '$sort': { 'total': -1 } }
            ]
        )
        aggregation_result_count = 0
        distinct_incomes = []
        for result in aggregation_results:
            aggregation_result_count += 1

            distinct_income = {
                'name': result[ '_id' ],
                'total': ( result[ 'total' ] )
            }
            distinct_incomes.append( distinct_income )

        return distinct_incomes


    def get_expense_total( _self, _start_date, _end_date ):
        expense_total = 0
        db = _self.get_database()

        matches_clause = {
            '$and':
            [
                { 'date': { '$gte': _start_date } },
                { 'date': { '$lt': _end_date } },
                { 'bucket': { '$regex': 'expense_.*' } }
            ]
        }
        group_clause = {
            '_id': '$bucket',
            'total': { '$sum': '$amount' }
        }
        group_clause_2 = {
            '_id': '_id',
            'total': { '$sum': '$total' }
        }
        #aggregation_results = db.test_transactions.aggregate(
        aggregation_results = db.transactions.aggregate(
            [
                { '$match': matches_clause },
                { '$group': group_clause },
                { '$sort': { 'total': 1 } },
                { '$group': group_clause_2 }
            ]
        )
        aggregation_result_count = 0
        distinct_expenses = []
        for result in aggregation_results:
            aggregation_result_count += 1
            expense_total += ( result[ 'total' ] * -1 )

        return expense_total


    def get_income_total( _self, _start_date, _end_date ):
        income_total = 0
        db = _self.get_database()

        matches_clause = {
            '$and':
            [
                { 'date': { '$gte': _start_date } },
                { 'date': { '$lt': _end_date } },
                { 'bucket': { '$regex': 'income_.*' } }
            ]
        }
        group_clause = {
            '_id': '$bucket',
            'total': { '$sum': '$amount' }
        }
        group_clause_2 = {
            '_id': '_id',
            'total': { '$sum': '$total' }
        }
        #aggregation_results = db.test_transactions.aggregate(
        aggregation_results = db.transactions.aggregate(
            [
                { '$match': matches_clause },
                { '$group': group_clause },
                { '$sort': { 'total': 1 } },
                { '$group': group_clause_2 }
            ]
        )
        for result in aggregation_results:
            income_total += ( result[ 'total' ] )

        return income_total


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

    def get_expense_bucket_totals( _self, _start_date, _end_date ):
        bucket_totals = [
            { '_id': 'expense_misc', 'total': 3024.17 },
            { '_id': 'expense_dining', 'total': 1258.21 },
            { '_id': 'expense_clothing', 'total': 456.23 }
        ]

        return bucket_totals

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


