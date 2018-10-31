#!/bin/python

import transactions.translation.mint.csv as mint_csv
#import chase.csv.checking
#import chase.csv.credit

def get_translator( _file_format ):
    if _file_format == 'mint-csv':
        return mint_csv.MintCsvTranslator()

