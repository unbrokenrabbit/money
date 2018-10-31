import transactions.translation.mint.csv as mint_csv
import transactions.transaction

PASS = '  pass  '
FAIL = '**FAIL**'

def run_all_tests():
    #test_are_columns_valid()
    #test_translate_from_file()
    test_translate_from_file_large()

def test_translate_from_file():
    print( 'test translate_from_file()' )
    mint_csv_translator = mint_csv.MintCsvTranslator()
    parsed_transactions = mint_csv_translator.translate_from_file( 'test/samples/transactions.csv' )
    print( 'transactions:', str( parsed_transactions ) )
    expected_transactions = [
        transactions.transaction.Transaction(
            _date = "10/23/2018",
            _description = "Hickory Pit",
            _original_description = "THE HICKORY PIT",
            _amount = "11.56",
            _transaction_type = "debit",
            _category = "Fast Food",
            _account = "credit_spending",
            _labels = "",
            _notes = ""
        ),
        transactions.transaction.Transaction(
            _date = "5/02/2017",
            _description = "Jasna Ligueno",
            _original_description = "Jasna Ligueno",
            _amount = "100.00",
            _transaction_type = "debit",
            _category = "Cash & ATM",
            _account = "checking_savings",
            _labels = "",
            _notes = ""
        )
    ]
    assert len( expected_transactions ) == len( parsed_transactions )
    for index in range( 0, len( expected_transactions ) ):
        expected_transaction = expected_transactions[ index ]
        transaction = parsed_transactions[ index ]
        assert transaction.is_match( expected_transaction )
        #for key in expected_transaction:
        #    assert expected_transaction[ key ] == transaction[ key ]
    
def test_translate_from_file_large():
    print( 'test translate_from_file_large()' )
    mint_csv_translator = mint_csv.MintCsvTranslator()
    parsed_transactions = mint_csv_translator.translate_from_file( 'test/samples/transactions_large.csv' )
    print( 'done' )

def test_are_columns_valid():
    print( 'test are_columns_valid()' )
    mint_csv_translator = mint_csv.MintCsvTranslator()

    valid_columns = '"Date","Description","Original Description","Amount","Transaction Type","Category","Account Name","Labels","Notes"\n'
    VALID_COLUMNS_MESSAGE = 'parse valid columns'
    try:
        assert mint_csv_translator.are_columns_valid( valid_columns )
        print( PASS, VALID_COLUMNS_MESSAGE )
    except:
        print( FAIL, VALID_COLUMNS_MESSAGE )

    invalid_columns_001 = 'invalid'
    INVALID_COLUMNS_MESSAGE = 'parse invalid columns'
    try:
        assert not mint_csv_translator.are_columns_valid( invalid_columns_001 )
        print( PASS, INVALID_COLUMNS_MESSAGE )
    except:
        print( FAIL, INVALID_COLUMNS_MESSAGE )
        
