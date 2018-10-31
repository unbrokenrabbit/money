#!/bin/bash

import transactions.translation.factory as translation_factory
import datastore.factory as datastore_factory

def import_transactions( _file_format, _path_to_file, _account ):
    translator = translation_factory.get_translator( _file_format )
    transactions = translator.translate_from_file( _path_to_file )

    datastore = datastore_factory.get_datastore()
    upsert_result = datastore.upsert_transactions( _account, transactions )

    return upsert_result

def remove_all_transactions():
    datastore = datastore_factory.get_datastore()

    return datastore.remove_all_transactions()
    
