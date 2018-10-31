
import datastore.factory as datastore_factory

def retrieve_transactions():
    datastore = datastore_factory.get_datastore()

    return datastore.retrieve_transactions()
