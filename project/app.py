from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import send_file
from flask import url_for
from werkzeug import secure_filename

import json
import mint.importer
import datastore.factory as datastore_factory
import datastore.bucket as datastore_bucket
import re
import logging


DATABASE_NAME = 'money_db'


app = Flask(__name__)
app.logger.setLevel( logging.DEBUG )


def get_datastore():
    return datastore_factory.get_datastore( 'money-mysql' )


@app.route( '/' )
def home():
    return render_template( 'home.html' )


@app.route( '/import-transactions', methods=['GET', 'POST'] )
def import_transactions():
    debug = {}
    updated_transaction_count = '0'
    new_transaction_count = '0'
    if request.method == 'POST':
        # Save the provided file on the filesystem
        if 'file' in request.files:
            transactions_file = request.files[ 'file' ]
            filename = secure_filename( transactions_file.filename )
            transactions_file.save( filename )

            importer = mint.importer.CsvImporter()
            transactions = importer.translate_from_file( filename )

            datastore = get_datastore()
            upsert_result = datastore.upsert_transactions( transactions )
            updated_transaction_count = upsert_result[ 'updated_transaction_count' ]
            new_transaction_count = upsert_result[ 'new_transaction_count' ]

            datastore.match_buckets_to_transactions()

    return render_template(
        'import-transactions.html',
        updated_transaction_count=updated_transaction_count,
        new_transaction_count=new_transaction_count,
        debug=debug
    )


@app.route( '/add-bucket', methods=['GET', 'POST'] )
def add_bucket():
    datastore = get_datastore()

    debug = {}
    if request.method == 'POST':
        #bucket = datastore_bucket.Bucket(
        #        _name = request.form[ 'bucket_name' ],
        #        _pattern = request.form[ 'bucket_pattern' ],
        #        _account = request.form[ 'bucket_account' ],
        #        _direction = request.form[ 'bucket_direction' ]
        #)
        #
        #result = datastore.add_bucket( bucket )
        result = datastore.add_bucket(
                request.form[ 'bucket_name' ],
                request.form[ 'bucket_account' ],
                request.form[ 'bucket_direction' ],
                request.form[ 'bucket_pattern' ]
        )
        datastore.match_buckets_to_transactions()
        datastore.set_bucket_import_settings( request.form[ 'bucket_account' ], request.form[ 'bucket_direction' ] )

        debug[ 'result' ] = result

    buckets = datastore.get_buckets()
    accounts = datastore.get_accounts()
    unapproved_transactions = datastore.get_unapproved_transactions()
    unbucketed_transactions = datastore.get_unbucketed_transactions()
    bucket_import_settings = datastore.get_bucket_import_settings()

    debug[ 'bucket_import_settings' ] = bucket_import_settings

    return render_template(
            'buckets.html',
            buckets=buckets,
            accounts=accounts,
            unapproved_transactions=unapproved_transactions,
            unbucketed_transactions=unbucketed_transactions,
            bucket_import_settings=bucket_import_settings,
            debug=debug
    )


@app.route( '/remove-bucket', methods=['GET', 'POST'] )
def remove_bucket():
    datastore = get_datastore()

    if request.method == 'POST':
        debug = ''
        for key in request.form:
            if( key.startswith( 'remove-bucket-button.' ) ):
                bucket_id = key[ len( 'remove-bucket-button.' ): ]
                result = datastore.remove_bucket( bucket_id )
                debug += "[" + bucket_id + "], " + str( result )

    buckets = datastore.get_buckets()
    accounts = datastore.get_accounts()
    unbucketed_transactions = datastore.get_unbucketed_transactions()
    bucket_import_settings = datastore.get_bucket_import_settings()

    return render_template(
            'buckets.html',
            buckets=buckets,
            accounts=accounts,
            bucket_import_settings=bucket_import_settings,
            debug=debug
    )


@app.route( '/buckets', methods=['GET', 'POST'] )
def buckets():
    debug = {}

    datastore = get_datastore()
    buckets = datastore.get_buckets()
    accounts = datastore.get_accounts()
    unapproved_transactions = datastore.get_unapproved_transactions()
    unbucketed_transactions = datastore.get_unbucketed_transactions()
    bucket_import_settings = datastore.get_bucket_import_settings()

    debug[ 'bucket_import_settings' ] = bucket_import_settings

    return render_template(
            'buckets.html',
            buckets=buckets,
            accounts=accounts,
            unapproved_transactions=unapproved_transactions,
            unbucketed_transactions=unbucketed_transactions,
            bucket_import_settings=bucket_import_settings,
            debug=debug
    )


@app.route( '/export-buckets', methods=[ 'POST' ] )
def export_buckets():
    datastore = get_datastore()
    buckets = datastore.get_buckets()

    buckets_dict = {
        'buckets': []
    }
    #buckets_list = []
    for bucket in buckets:
        buckets_dict[ 'buckets' ].append( bucket.to_dict() )

    OUTPUT_FILE_NAME = 'buckets.json'
    output_file = open( OUTPUT_FILE_NAME, 'w' )
    json.dump( buckets_dict, output_file, indent=4 )
    output_file.close()

    return send_file( OUTPUT_FILE_NAME, as_attachment=True, attachment_filename=OUTPUT_FILE_NAME )


@app.route( '/import-buckets', methods=['GET', 'POST'] )
def import_buckets():
    datastore = get_datastore()

    debug = {
            'updated_bucket_count': 0,
            'new_bucket_count': 0,
            'imported_buckets': []
    }

    if request.method == 'POST':

        # Save the provided file on the filesystem
        if 'file' in request.files:
            buckets_file = request.files[ 'file' ]
            filename = secure_filename( buckets_file.filename )
            buckets_file.save( filename )

            buckets_file_input = open( filename, 'r' )
            buckets_dict = json.load( buckets_file_input )

            for bucket_dict in buckets_dict[ 'buckets' ]:
                #bucket = datastore_bucket.Bucket()
                #bucket.from_dict( bucket_dict )

                #datastore.add_bucket( bucket )
                result = datastore.add_bucket(
                        bucket_dict[ 'name' ],
                        bucket_dict[ 'account' ],
                        bucket_dict[ 'direction' ],
                        bucket_dict[ 'pattern' ]
                )

                debug[ 'new_bucket_count' ] += result[ 'new_bucket_count' ]
                debug[ 'updated_bucket_count' ] += result[ 'updated_bucket_count' ]
                debug[ 'imported_buckets' ].append( bucket_dict )

            datastore.match_buckets_to_transactions()

    buckets = datastore.get_buckets()
    accounts = datastore.get_accounts()
    unapproved_transactions = datastore.get_unapproved_transactions()
    unbucketed_transactions = datastore.get_unbucketed_transactions()
    bucket_import_settings = datastore.get_bucket_import_settings()

    return render_template(
            'buckets.html',
            buckets=buckets,
            accounts=accounts,
            unapproved_transactions=unapproved_transactions,
            unbucketed_transactions=unbucketed_transactions,
            bucket_import_settings=bucket_import_settings,
            debug=debug
    )

import datetime

@app.route( '/breakdown' )
def _breakdown():
    datastore = get_datastore()
    
    years = {}
    months = []
    debug = []

    min_date = datetime.datetime( 2017, 1, 1 )
    max_date = datetime.datetime.now()

    current_month_start = datetime.datetime( max_date.year, max_date.month, 1 )
    next_month_start = current_month_start + datetime.timedelta( days=31 )
    next_month_start = next_month_start.replace( day=1 )
    while( current_month_start > min_date ):
        current_month = {}
        current_month[ 'title' ] = current_month_start.strftime( '%B %Y' )
        current_month[ 'transactions' ] = datastore.retrieve_transactions(
                _start_date=current_month_start,
                _end_date=next_month_start
        )
        current_month[ 'distinct_expenses' ] = datastore.get_distinct_expenses(
                _start_date=current_month_start,
                _end_date=next_month_start
        )
        if( len( current_month[ 'distinct_expenses' ] ) > 0 ):
            current_month[ 'distinct_expenses_max' ] = ( int( current_month[ 'distinct_expenses' ][ 0 ][ 'total' ] / 1000 ) + 1 ) * 1000
        else:
            current_month[ 'distinct_expenses_max' ] = 0

        current_month[ 'expense_total' ] = datastore.get_expense_total(
                _start_date=current_month_start,
                _end_date=next_month_start
        )

        current_month[ 'distinct_incomes' ] = datastore.get_distinct_incomes(
                _start_date=current_month_start,
                _end_date=next_month_start
        )
        if( len( current_month[ 'distinct_incomes' ] ) > 0 ):
            current_month[ 'distinct_incomes_max' ] = ( int( current_month[ 'distinct_incomes' ][ 0 ][ 'total' ] / 1000 ) + 1 ) * 1000
        else:
            current_month[ 'distinct_incomes_max' ] = 0

        current_month[ 'income_total' ] = datastore.get_income_total(
                _start_date=current_month_start,
                _end_date=next_month_start
        )

        months.append( current_month )

        if( current_month_start.year in years ):
            current_year = years[ current_month_start.year ]
        else:
            current_year = {
                'monthly_income_totals': [],
                'monthly_expense_totals': []
            }
            for month in range( 12 ):
                current_year[ 'monthly_income_totals' ].append( 0 )
                current_year[ 'monthly_expense_totals' ].append( 0 )

        month_index = current_month_start.month - 1
        current_year[ 'monthly_income_totals' ][ month_index ] = datastore.get_income_total( current_month_start, next_month_start )
        current_year[ 'monthly_expense_totals' ][ month_index ] = datastore.get_expense_total( current_month_start, next_month_start )

        years[ current_month_start.year ] = current_year

        delta = datetime.timedelta( days=1 )
        current_month_start = current_month_start - delta
        current_month_start = current_month_start.replace( day=1 )
        next_month_start = next_month_start - delta
        next_month_start = next_month_start.replace( day=1 )

    yearly_breakdowns = []
    for key in years:
        monthly_income_max = max( years[ key ][ 'monthly_income_totals' ] )
        monthly_expense_max = max( years[ key ][ 'monthly_expense_totals' ] )
        maximums = [ monthly_income_max, monthly_expense_max ]
        yearly_breakdown = {
            'year': key,
            'monthly_income_totals': years[ key ][ 'monthly_income_totals' ],
            'monthly_income_max': monthly_income_max,
            'monthly_expense_totals': years[ key ][ 'monthly_expense_totals' ],
            'monthly_expense_max': monthly_expense_max,
            'overall_max': max( maximums ),
            'income_total': sum( years[ key ][ 'monthly_income_totals' ] ),
            'expense_total': sum( years[ key ][ 'monthly_expense_totals' ] )
        }
        yearly_breakdowns.append( yearly_breakdown )

    return render_template(
            'breakdown.html',
            max=300,
            monthly_breakdowns=months,
            yearly_breakdowns=yearly_breakdowns,
            debug=yearly_breakdowns
    )

@app.route( '/debug' )
def debug():
    datastore = get_datastore()

    transactions = datastore.retrieve_transactions()

    labels = [
        'label1',
        'label2'
    ]

    values = [
        100,
        200
    ]

    return render_template(
            'debug.html',
            transactions=transactions,
            max=300,
            labels=labels,
            values=values
    )


@app.route( '/debug-remove-all-transactions', methods=['GET', 'POST'] )
def debug_remove_all_transactions():
    if request.method == 'POST':
        #transactions_removed_count = transactions.importer.remove_all_transactions()
        datastore = get_datastore()
        transactions_removed_count = datastore.remove_all_transactions()

    return render_template( 'debug.html', transactions_removed_count=transactions_removed_count )


#def match_buckets_to_transactions():
#    datastore = get_datastore()
#
#    # Get all unbucketed transactions
#    unbucketed_transactions = datastore.get_unbucketed_transactions()
#
#    # Get all buckets
#    buckets = datastore.get_buckets()
#
#    for unbucketed_transaction in unbucketed_transactions:
#        for bucket in buckets:
#            if( re.match( bucket.pattern, unbucketed_transaction.description ) ):
#                datastore.apply_bucket_to_transaction( unbucketed_transaction, bucket, 'unapproved' )


@app.route( '/debug-initialize-database', methods=['GET', 'POST'] )
def debug_initialize_database():
    if request.method == 'POST':
        datastore = get_datastore()
        datastore.initialize_database()

    return render_template( 'debug.html' )


if __name__ == "__main__":
    app.run( host="0.0.0.0", debug=True )
