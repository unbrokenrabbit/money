#!/bin/bash

import transactions.transaction

class MintCsvTranslator:
    def __init__( _self ):
        _self.test = 0

    def debug( _self ):
        return 'I translate Mint CSV files'

    def translate_from_file( _self, _path_to_file ):
        print( 'hi there' )

        debug_buffered_line_count = 0
        debug_appended_line_count = 0

        parsed_transactions = []

        transactions_file = open( _path_to_file, 'r' )
        columns_string = transactions_file.readline()

        if _self.are_columns_valid( columns_string ):
            current_date = ''
            lines_to_process = {}
            
            # DEBUG
            debug_line_count = 0

            while True:
                line = transactions_file.readline()
                if not line:
                    # End of file reached, process all remaining lines and exit loop
                    for line_to_process in lines_to_process:
                        transaction_values = line_to_process.split( ',' )

                        for index in range( lines_to_process[ line_to_process ] + 1 ):
                            transaction = transactions.transaction.Transaction()

                            transaction.date = transaction_values[ 0 ]
                            transaction.description = transaction_values[ 1 ]
                            transaction.original_description = transaction_values[ 2 ]
                            transaction.amount = transaction_values[ 3 ]
                            transaction.transaction_type = transaction_values[ 4 ]
                            transaction.category = transaction_values[ 5 ]
                            transaction.account = transaction_values[ 6 ]
                            transaction.labels = transaction_values[ 7 ]
                            transaction.notes = transaction_values[ 8 ]
                            transaction.instance = index

                            # DEBUG
                            if( index > 0 ):
                                print( 'index:', index )

                            parsed_transactions.append( transaction )

                            # DEBUG
                            debug_appended_line_count += 1
                            #print( 'appended line count:', str( debug_appended_line_count ) )

                            #print( '-', line_to_process )

                    current_date = new_date
                    lines_to_process.clear()
                    break

                modified_line = line.replace( '"', '' )
                modified_line = modified_line.rstrip()

                transaction_values = modified_line.split( ',' )


                # DEBUG
                debug_line_count += 1
                debug_buffered_line_count += 1
                #print( 'buffered line count:', str( debug_buffered_line_count ) )

                new_date = transaction_values[ 0 ]
                if( current_date == new_date ):
                    #print( '+', modified_line )
                    if( modified_line in lines_to_process ):
                        lines_to_process[ modified_line ] += 1
                    else:
                        lines_to_process[ modified_line ] = 0
                else:
                    for line_to_process in lines_to_process:
                        transaction_values = line_to_process.split( ',' )

                        for index in range( lines_to_process[ line_to_process ] + 1 ):
                            transaction = transactions.transaction.Transaction()

                            transaction.date = transaction_values[ 0 ]
                            transaction.description = transaction_values[ 1 ]
                            transaction.original_description = transaction_values[ 2 ]
                            transaction.amount = transaction_values[ 3 ]
                            transaction.transaction_type = transaction_values[ 4 ]
                            transaction.category = transaction_values[ 5 ]
                            transaction.account = transaction_values[ 6 ]
                            transaction.labels = transaction_values[ 7 ]
                            transaction.notes = transaction_values[ 8 ]
                            transaction.instance = index

                            # DEBUG
                            if( index > 0 ):
                                print( 'index:', index )

                            parsed_transactions.append( transaction )

                            # DEBUG
                            debug_appended_line_count += 1
                            #print( 'appended line count:', str( debug_appended_line_count ) )

                            #print( '-', line_to_process )

                    current_date = new_date
                    lines_to_process.clear()

                    #print( '+', modified_line )
                    lines_to_process[ modified_line ] = 0

                #print( 'delta:', str( debug_buffered_line_count - debug_appended_line_count ) )
        else:
            raise ValueError( 'Invalid column values' )

        print( 'line count:', str( debug_line_count ) )
        print( 'transaction count:', str( len( parsed_transactions ) ) )
        print( 'lines to process count:', str( len( lines_to_process ) ) )

        return parsed_transactions

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


