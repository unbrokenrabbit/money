import unittest
import datastore.factory
import datastore.bucket
#import datetime
import io
import sys

class TestCsvImporter( unittest.TestCase ):
    
    def get_datastore( _self ):
        return datastore.factory.get_datastore( 'money-mysql-test' )

    def test_is_bucket_present_001( _self ):
        db = _self.get_datastore()
        db.initialize_database()

        bucket = datastore.bucket.Bucket(
            _name = 'bill_comics',
            _pattern = 'beyond tomorrow comics',
            _account = 'credit_spending',
            _direction = 'expense'
        )
        _self.assertFalse( db.is_bucket_present( bucket ) )

    def test_add_bucket_001( _self ):
        db = _self.get_datastore()
        db.initialize_database()

        bucket = datastore.bucket.Bucket(
            _name = 'bill_comics',
            _pattern = 'beyond tomorrow comics',
            _account = 'credit_spending',
            _direction = 'expense'
        )

        db.add_bucket( bucket )

        _self.assertTrue( db.is_bucket_present( bucket ) )

if __name__ == '__main__':
    unittest.main()
