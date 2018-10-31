import transactions.translation.mint.csv as mint_csv

def test_001():
    print( 'test 001' )
    mint_csv_translator = mint_csv.MintCsvTranslator()

    valid_columns = '"Date","Description","Original Description","Amount","Transaction Type","Category","Account Name","Labels","Notes"\n'
    assert mint_csv_translator.are_columns_valid( valid_columns )
    print( 'pass' )

    invalid_columns_001 = 'invalid'
    assert not mint_csv_translator.are_columns_valid( invalid_columns_001 )
    print( 'pass )
