from pymongo import MongoClient
import pymongo
import transactions.transaction as trans

class MongoManager:
    #def upsert_transactions( _self, _transactions ):
    #    raise RuntimeError( 'MongoManager.upsert_transactions() not implemented' )

    def get_database( _self ):
        mongo_client = MongoClient( 'money-mongodb' )

        return  mongo_client.money_db

    def upsert_transactions( _self, _account, _transactions ):
        db = _self.get_database()
    
        # DEBUG
        debug_updated_transactions = []

        new_transaction_count = 0
        updated_transaction_count = 0
        for transaction in _transactions:
            row = {}
            row[ 'account' ] = transaction.account
            row[ 'type' ] = transaction.transaction_type
            row[ 'date' ] = transaction.date
            row[ 'amount' ] = transaction.amount
            row[ 'balance' ] = '0'
            row[ 'description' ] = transaction.description
            row[ 'original_description' ] = transaction.original_description
            row[ 'category' ] = transaction.category
            row[ 'notes' ] = transaction.notes
            row[ 'instance' ] = transaction.instance
            #row[ 'labels' ] = transaction.labels

            update_result = db.transactions.update(
                row,
                {
                    "$set": row,
                },
                upsert = True
            )

            if( update_result[ 'updatedExisting' ] ):
                updated_transaction_count += 1

                # DEBUG
                debug_updated_transactions.append( transaction )
            else:
                new_transaction_count += 1

        result = {}
        result[ 'updated_transaction_count' ] = updated_transaction_count
        result[ 'new_transaction_count' ] = new_transaction_count
        
        # DEBUG
        result[ 'debug_updated_transactions' ] = debug_updated_transactions

        return result

    def retrieve_transactions( _self ):
        db = _self.get_database()
        
        transactions = []
        results = db.transactions.find()
        for result in results:
            transaction = trans.Transaction(
                _account = result[ 'account' ],
                _transaction_type = result[ 'type' ],
                _date = result[ 'date' ],
                _amount = result[ 'amount' ],
                #_balance = result[ 'balance' ,
                _description = result[ 'description' ],
                _original_description = result[ 'original_description' ],
                _category = result[ 'category' ],
                _notes = result[ 'notes' ],
                _instance = result[ 'instance' ]
            )

            transactions.append( transaction )

        return transactions

    def remove_all_transactions( _self ):
        db = _self.get_database()
        result = db.transactions.remove()

        return result[ 'n' ]
        
