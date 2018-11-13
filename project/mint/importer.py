import datastore.transaction
import datetime

class CsvImporter:
    def __init__( _self ):
        _self.test = 0

    def debug( _self ):
        return 'I translate Mint CSV files'

    def translate_from_file( _self, _path_to_file ):
        parsed_transactions = []

        transactions_file = open( _path_to_file, 'r' )
        columns_string = transactions_file.readline()

        if _self.are_columns_valid( columns_string ):
            current_date = ''
            lines_to_process = {}
            
            while True:
                new_line = transactions_file.readline()
                if not new_line:
                    # End of file reached, process all remaining lines and exit loop
                    _self.process_queued_lines( lines_to_process, parsed_transactions )
                    current_date = new_date
                    break

                temp_transaction = _self.translate_line( new_line )
                new_date = temp_transaction.date

                if( current_date == new_date ):
                    if( new_line in lines_to_process ):
                        lines_to_process[ new_line ] += 1
                    else:
                        lines_to_process[ new_line ] = 0
                else:
                    _self.process_queued_lines( lines_to_process, parsed_transactions )
                    current_date = new_date
                    lines_to_process[ new_line ] = 0
        else:
            raise ValueError( 'Invalid column values' )

        return parsed_transactions

    def process_queued_lines( _self, _lines_to_process, _parsed_transactions ):
        for line_to_process in _lines_to_process:
            for index in range( _lines_to_process[ line_to_process ] + 1 ):
                transaction = _self.translate_line( line_to_process )
                transaction.instance = index
        
                _parsed_transactions.append( transaction )
        
        #current_date = new_date
        _lines_to_process.clear()

    def translate_line( _self, _input_line ):
        trimmed_input_line = _input_line[ 1:-1 ]
        values = trimmed_input_line.split( '","' )

        transaction = datastore.transaction.Transaction()
        transaction.date = datetime.datetime.strptime( values[ 0 ], '%m/%d/%Y' )
        transaction.description = values[ 2 ]
        transaction.amount = float( values[ 3 ] )
        transaction_type = values[ 4 ]
        transaction.account = values[ 6 ]

        if( transaction_type == 'debit' ):
            transaction.amount *= -1

        return transaction

    def are_columns_valid( _self, _columns_string ):
        modified_columns_string = _columns_string.replace( '"', '' )
        modified_columns_string = modified_columns_string.rstrip()
        columns = modified_columns_string.split( ',' )

        expected_columns = [
            'Date',
            'Description',
            'Original Description',
            'Amount',
            'Transaction Type',
            'Category',
            'Account Name',
            'Labels',
            'Notes'
        ] 
        if( len( columns ) == len( expected_columns ) ):
            is_valid = True
            for index in range( 0, len( columns ) ):
                if( columns[ index ] != expected_columns[ index ] ):
                    is_valid = False
                    break
        else:
            is_valid = False

        return is_valid


