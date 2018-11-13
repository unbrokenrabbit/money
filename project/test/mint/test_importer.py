import unittest
import mint.importer
import datastore.transaction
import datetime
import io
import sys

class TestCsvImporter( unittest.TestCase ):
        
    def test_translate_line_001( _self ):
        input_line = '"10/07/2018","Nashville Paint Pros","NASHVILLE PAINTBALL, INC","50.00","debit","Home Improvement","credit_spending","",""'
        importer = mint.importer.CsvImporter()
        translated_transaction = importer.translate_line( input_line )       

        expected_transaction = datastore.transaction.Transaction(
            _date = datetime.datetime.strptime( '10/07/2018', "%m/%d/%Y" ),
            _description = 'NASHVILLE PAINTBALL, INC',
            _amount = 50.00,
            _account = 'credit_spending'
        )

        _self.assertTrue( translated_transaction.is_match( expected_transaction ) )

    def test_translate_line_002( _self ):
        input_line = '"6/15/2018","Toys ""R"" Us","TOYS R US #6022","128.14","debit","Toys","credit_spending","",""'
        importer = mint.importer.CsvImporter()
        translated_transaction = importer.translate_line( input_line )       

        expected_transaction = datastore.transaction.Transaction(
            _date = datetime.datetime.strptime( '6/15/2018', "%m/%d/%Y" ),
            _description = 'TOYS R US #6022',
            _amount = 128.14,
            _account = 'credit_spending'
        )

        _self.assertTrue( translated_transaction.is_match( expected_transaction ) )

    def test_translate_line_003( _self ):
        input_line = '"6/15/2018","Toys ""R"" Us","TOYS R US #6022","128.14","debit","Toys","credit_spending","","blah"'
        importer = mint.importer.CsvImporter()
        translated_transaction = importer.translate_line( input_line )       

        expected_transaction = datastore.transaction.Transaction(
            _date = datetime.datetime.strptime( '6/15/2018', "%m/%d/%Y" ),
            _description = 'TOYS R US #6022',
            _amount = 128.14,
            _account = 'credit_spending'
        )

        _self.assertTrue( translated_transaction.is_match( expected_transaction ) )

    def test_translate_from_file_001( _self ):
        importer = mint.importer.CsvImporter()
        importer.translate_from_file( 'test/samples/transactions_001.csv' )

        
if __name__ == '__main__':
    unittest.main()
