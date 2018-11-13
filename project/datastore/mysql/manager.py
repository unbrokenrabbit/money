import mysql.connector
import datastore.transaction

class MysqlManager:

    def __init__( _self, _database_server ):
        _self.database_server = _database_server
        

    def get_database( _self ):
        database = mysql.connector.connect(
            host = _self.database_server,
            user = "money_user",
            passwd = "money_password",
            database = "money_db"
        )

        return database

    def initialize_database( _self ):
        db = _self.get_database()

        cursor = db.cursor()
        cursor.execute( 'DROP TABLE IF EXISTS transactions' )
        cursor.execute( 'DROP TABLE IF EXISTS buckets' )
        cursor.execute( 'DROP TABLE IF EXISTS bucket_names' )
        cursor.execute( 'DROP TABLE IF EXISTS bucket_rules' )

        create_bucket_rules_table_command = ''
        create_bucket_rules_table_command += 'CREATE TABLE bucket_rules ('
        create_bucket_rules_table_command += '      id INT AUTO_INCREMENT PRIMARY KEY'
        create_bucket_rules_table_command += '    , pattern VARCHAR( 255 )'
        create_bucket_rules_table_command += '    , account VARCHAR( 255 )'
        create_bucket_rules_table_command += '    , direction ENUM( "income", "expense" )'
        create_bucket_rules_table_command += '    , UNIQUE('
        create_bucket_rules_table_command += '          pattern'
        create_bucket_rules_table_command += '        , account'
        create_bucket_rules_table_command += '        , direction'
        create_bucket_rules_table_command += '    )'
        create_bucket_rules_table_command += ' )'
        cursor.execute( create_bucket_rules_table_command )

        create_bucket_names_table_command = ''
        create_bucket_names_table_command += 'CREATE TABLE bucket_names ('
        create_bucket_names_table_command += '      id INT AUTO_INCREMENT PRIMARY KEY'
        create_bucket_names_table_command += '    , name VARCHAR(255)'
        create_bucket_names_table_command += '          NOT NULL'
        create_bucket_names_table_command += '          UNIQUE'
        create_bucket_names_table_command += ' )'
        cursor.execute( create_bucket_names_table_command )

        create_buckets_table_command = ''
        create_buckets_table_command += 'CREATE TABLE buckets ('
        create_buckets_table_command += '      id INT'
        create_buckets_table_command += '          AUTO_INCREMENT'
        create_buckets_table_command += '          PRIMARY KEY'
        create_buckets_table_command += '    , bucket_name INT NOT NULL'
        create_buckets_table_command += '    , bucket_rule INT NOT NULL'
        create_buckets_table_command += '    , FOREIGN KEY fk_bucket_name( bucket_name )'
        create_buckets_table_command += '          REFERENCES bucket_names( id )'
        create_buckets_table_command += '          ON UPDATE CASCADE'
        create_buckets_table_command += '          ON DELETE RESTRICT'
        create_buckets_table_command += '    , FOREIGN KEY fk_bucket_rule( bucket_rule )'
        create_buckets_table_command += '          REFERENCES bucket_rules( id )'
        create_buckets_table_command += '          ON UPDATE CASCADE'
        create_buckets_table_command += '          ON DELETE RESTRICT'
        create_buckets_table_command += ' )'
        cursor.execute( create_buckets_table_command )

        create_transactions_table_command = ''
        create_transactions_table_command += 'CREATE TABLE transactions ('
        create_transactions_table_command += '      transaction_date DATE'
        create_transactions_table_command += '    , description VARCHAR( 255 )'
        create_transactions_table_command += '    , amount DECIMAL( 15, 2 )'
        create_transactions_table_command += '    , account VARCHAR( 255 )'
        create_transactions_table_command += '    , instance INT'
        create_transactions_table_command += '    , bucket INT'
        create_transactions_table_command += '          DEFAULT NULL'
        create_transactions_table_command += '    , bucket_status ENUM( "approved", "unapproved" )'
        create_transactions_table_command += '    , PRIMARY KEY('
        create_transactions_table_command += '            transaction_date'
        create_transactions_table_command += '          , description'
        create_transactions_table_command += '          , amount'
        create_transactions_table_command += '          , account'
        create_transactions_table_command += '          , instance'
        create_transactions_table_command += '      )'
        create_transactions_table_command += '    , FOREIGN KEY fk_bucket( bucket )'
        create_transactions_table_command += '          REFERENCES buckets( id )'
        create_transactions_table_command += '          ON UPDATE CASCADE'
        create_transactions_table_command += '          ON DELETE CASCADE'
        create_transactions_table_command += ')'
        cursor.execute( create_transactions_table_command )

        db.commit()

        cursor.close()
        db.close()

        return ''

    def upsert_transactions( _self, _transactions ):
        db = _self.get_database()

        for transaction in _transactions:
            cursor = db.cursor()
            command = ''
            command += 'INSERT INTO transactions ('
            command += '      transaction_date'
            command += '    , description'
            command += '    , amount'
            command += '    , account'
            command += '    , instance'
            command += ' )'
            command += 'VALUES ('
            command += '      %s'
            command += '    , %s'
            command += '    , %s'
            command += '    , %s'
            command += '    , %s'
            command += ')'
            command += ' ON DUPLICATE KEY UPDATE description=description'
            values = (
                transaction.date.isoformat(),
                transaction.description,
                transaction.amount,
                transaction.account,
                transaction.instance
            )

            cursor.execute( command, values )
            cursor.close()
 
        db.commit()

        cursor.close()
        db.close()           

        result = {}

        return result

    def retrieve_transactions( _self ):
        db = _self.get_database()

        transactions = []
        query = 'SELECT transaction_date, description, amount, account, instance, bucket FROM transactions'
        cursor = db.cursor()
        try:
            cursor.execute( query )
            rows = cursor.fetchall()
            #print( 'transaction rows:', cursor.rowcount )

            for row in rows:
                transaction = datastore.transaction.Transaction()
                transaction.date = row[ 0 ]
                transaction.description = row[ 1 ]
                transaction.amount = row[ 2 ]
                transaction.account = row[ 3 ]
                transaction.instance = row[ 4 ]
                transaction.bucket = row[ 5 ]

                transactions.append( transaction )
        except:
            print( 'unable to retrieve transactions' )

        cursor.close()
        db.close()

        return transactions

    def apply_bucket_to_transaction( _self, _transaction, _bucket, _bucket_state='unapproved' ):
        update_command = ''
        update_command += ' UPDATE transactions'
        update_command += ' SET bucket=' + str( _bucket.id )
        update_command += ' WHERE'
        update_command += '     transaction_date="' + _transaction.date.isoformat() + '"'
        update_command += '     AND description="' + _transaction.description + '"'
        update_command += '     AND amount=' + str( _transaction.amount )
        update_command += '     AND account="' + _transaction.account + '"'
        update_command += '     AND instance=' + str( _transaction.instance )

        db = _self.get_database()

        cursor = db.cursor()       
        cursor.execute( update_command )
        db.commit()

        cursor.close()
        db.close()


    def get_unbucketed_transactions( _self ):
        db = _self.get_database()

        transactions = []
        query = 'SELECT transaction_date, description, amount, account, instance, bucket FROM transactions WHERE bucket IS NULL'
        cursor = db.cursor()
        try:
            cursor.execute( query )
            rows = cursor.fetchall()
            #print( 'transaction rows:', cursor.rowcount )

            for row in rows:
                transaction = datastore.transaction.Transaction()
                transaction.date = row[ 0 ]
                transaction.description = row[ 1 ]
                transaction.amount = row[ 2 ]
                transaction.account = row[ 3 ]
                transaction.instance = row[ 4 ]

                transactions.append( transaction )
        except:
            print( 'unable to retrieve transactions' )

        cursor.close()
        db.close()

        return transactions

    def remove_all_transactions( _self ):
        return 0
        
    def add_bucket( _self, _bucket ):
        if( not _self.is_bucket_present( _bucket ) ):
            bucket_name_id = None
            if( _self.is_bucket_name_present( _bucket.name ) ):
                bucket_name_id = _self.get_bucket_name_id( _bucket.name )
            else:
                bucket_name_id = _self.insert_bucket_name( _bucket.name )

            bucket_rule_id = _self.insert_bucket_rule(
                    _bucket.pattern,
                    _bucket.account,
                    _bucket.direction
            )

            bucket_id = _self.insert_bucket( bucket_name_id, bucket_rule_id )
        else:
            bucket_id = _self.get_bucket_id( _bucket )

    def get_bucket_id( _self, _bucket ):
        db = _self.get_database()

        query = _self.build_get_bucket_id_query( _bucket )
        cursor = db.cursor()
        cursor.execute( query )

        row = cursor.fetchone()

        bucket_id = row[ 0 ]

        cursor.close()
        db.close()

        return bucket_id

    def build_get_bucket_id_query( _self, _bucket ):
        query = ''
        query += 'SELECT b.id'
        query += '    FROM buckets AS b'
        query += '    INNER JOIN bucket_names AS n'
        query += '    ON b.bucket_name = n.id'
        query += '    INNER JOIN bucket_rules AS r'
        query += '    ON b.bucket_rule = r.id'
        query += '    WHERE n.name = "' + _bucket.name + '"'
        query += '        AND r.pattern = "' + _bucket.pattern + '"'
        query += '        AND r.account = "' + _bucket.account + '"'
        query += '        AND r.direction = "' + _bucket.direction + '"'

        return query

    def is_bucket_present( _self, _bucket ):
        db = _self.get_database()

        query = _self.build_get_bucket_id_query( _bucket )
        cursor = db.cursor()
        cursor.execute( query )

        row = cursor.fetchone()

        if( row is not None ):
            is_present = True
        else:
            is_present = False

        cursor.close()
        db.close()

        return is_present

    def is_bucket_name_present( _self, _bucket_name ):
        db = _self.get_database()

        query = ''
        query += 'SELECT name'
        query += '    FROM bucket_names'
        query += '    WHERE name = "' + _bucket_name + '"'
        cursor = db.cursor()
        cursor.execute( query )

        row = cursor.fetchone()

        if( row is not None ):
            is_present = True
        else:
            is_present = False

        cursor.close()
        db.close()

        return is_present

    def insert_bucket( _self, _bucket_name_id, _bucket_rule_id ):
        db = _self.get_database()

        cursor = db.cursor()
        bucket_command = ''
        bucket_command += 'INSERT INTO buckets ('
        bucket_command += '      bucket_name'
        bucket_command += '    , bucket_rule'
        bucket_command += ' )'
        bucket_command += 'VALUES ('
        bucket_command += '      %s'
        bucket_command += '    , %s'
        bucket_command += ')'
        bucket_command += ' ON DUPLICATE KEY UPDATE bucket_name=bucket_name'
        bucket_values = (
            _bucket_name_id,
            _bucket_rule_id
        )

        cursor.execute( bucket_command, bucket_values )
        bucket_id = cursor.lastrowid
 
        db.commit()

        cursor.close()
        db.close()

        return bucket_id

    def insert_bucket_name( _self, _name ):
        db = _self.get_database()

        cursor = db.cursor()
        bucket_names_command = ''
        bucket_names_command += 'INSERT INTO bucket_names ('
        bucket_names_command += '      name'
        bucket_names_command += ' )'
        bucket_names_command += 'VALUES ('
        bucket_names_command += '      %s'
        bucket_names_command += ')'
        bucket_names_values = (
            _name,
        )

        cursor.execute( bucket_names_command, bucket_names_values )
        bucket_names_id = cursor.lastrowid
 
        db.commit()

        cursor.close()
        db.close()

        return bucket_names_id

    def insert_bucket_rule( _self, _pattern, _account, _direction ):
        db = _self.get_database()

        cursor = db.cursor()
        bucket_rules_command = ''
        bucket_rules_command += 'INSERT INTO bucket_rules ('
        bucket_rules_command += '      pattern'
        bucket_rules_command += '    , account'
        bucket_rules_command += '    , direction'
        bucket_rules_command += ')'
        bucket_rules_command += 'VALUES ('
        bucket_rules_command += '      %s'
        bucket_rules_command += '    , %s'
        bucket_rules_command += '    , %s'
        bucket_rules_command += ')'
        bucket_rules_command += ' ON DUPLICATE KEY UPDATE direction=direction'
        bucket_rules_values = (
            _pattern,
            _account,
            _direction
        )

        cursor.execute( bucket_rules_command, bucket_rules_values )
        bucket_rules_id = cursor.lastrowid
 
        db.commit()

        cursor.close()
        db.close()

        return bucket_rules_id

    def remove_bucket( _self, _id ):
        return ''

    def get_bucket_name_id( _self, _bucket_name ):
        db = _self.get_database()

        buckets = []
        query = ''
        query += 'SELECT id'
        query += '    FROM bucket_names'
        query += '    WHERE name = "' + _bucket_name + '"'
        cursor = db.cursor()
        cursor.execute( query )

        row = cursor.fetchone()

        bucket_name_id = None
        if( row is not None ):
            bucket_name_id = row[ 0 ]

        cursor.close()
        db.close()

        return bucket_name_id

    def get_buckets( _self ):
        db = _self.get_database()

        buckets = []
        query = ''
        query += 'SELECT R.pattern, R.account, R.direction, N.name, B.id'
        query += '    FROM bucket_rules R'
        query += '    LEFT JOIN buckets B'
        query += '    ON R.id = B.bucket_rule'
        query += '    LEFT JOIN bucket_names N'
        query += '    ON N.id = B.bucket_name'
        cursor = db.cursor()
        cursor.execute( query )
        rows = cursor.fetchall()
        #print( 'transaction rows:', cursor.rowcount )

        for row in rows:
            bucket = datastore.bucket.Bucket()
            bucket.pattern = row[ 0 ]
            bucket.account = row[ 1 ]
            bucket.direction = row[ 2 ]
            bucket.name = row[ 3 ]
            bucket.id = row[ 4 ]

            buckets.append( bucket )

        cursor.close()
        db.close()

        return buckets

    def get_accounts( _self ):
        # TODO implement
        return [ 'checking_spending', 'checking_bills', 'savings', 'credit_spending', 'credit_bills' ]

