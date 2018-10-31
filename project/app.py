from flask import Flask
from flask import render_template
from flask import request
from werkzeug import secure_filename

import transactions.importer
import transactions.retriever as transactions_retriever

app = Flask(__name__)

@app.route( '/' )
def home():
    return render_template( 'home.html' )

@app.route( '/import-transactions', methods=['GET', 'POST'] )
def import_transactions():
    debug = {}
    updated_transaction_count = '0'
    new_transaction_count = '0'
    if request.method == 'POST':
        # Determine the format of the file
        file_format = request.form[ "format" ]

        # Determine the account
        account = request.form[ "account" ]

        debug[ 'file_format' ] = file_format

        # Save the provided file on the filesystem
        if 'file' in request.files:
            transactions_file = request.files[ 'file' ]
            filename = secure_filename( transactions_file.filename )
            transactions_file.save( filename )

            import_result = transactions.importer.import_transactions( file_format, filename, account )

            debug[ 'file' ] = transactions_file
            debug[ 'import_result' ] = import_result
            debug[ 'debug_updated_transactions' ] = import_result[ 'debug_updated_transactions' ]

            updated_transaction_count = import_result[ 'updated_transaction_count' ]
            new_transaction_count = import_result[ 'new_transaction_count' ]

    accounts = [
        'checking-spending',
        'checking-bills',
        'savings-primary',
        'credit-spending',
        'credit-bills'
    ]

    formats = [
        'mint-csv',
        'chase-csv-checking',
        'chase-csv-credit'
    ]

    return render_template(
        'import-transactions.html',
        accounts=accounts,
        formats=formats,
        updated_transaction_count=updated_transaction_count,
        new_transaction_count=new_transaction_count,
        debug=debug
    )

@app.route( '/debug' )
def debug():
    transactions = transactions_retriever.retrieve_transactions()

    return render_template( 'debug.html', transactions=transactions )

@app.route( '/debug-remove-all-transactions', methods=['GET', 'POST'] )
def debug_remove_all_transactions():
    if request.method == 'POST':
        transactions_removed_count = transactions.importer.remove_all_transactions()

    return render_template( 'debug.html', transactions_removed_count=transactions_removed_count )

if __name__ == "__main__":
    app.run( host="0.0.0.0", debug=True )
