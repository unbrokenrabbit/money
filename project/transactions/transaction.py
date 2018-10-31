
ERROR = 'ERROR'

class Transaction:
    def __init__( _self, _date='', _description='', _original_description='', _amount='', _transaction_type='', _category='', _account='', _labels='', _notes='', _instance=0 ):
        _self.date = _date
        _self.description = _description
        _self.original_description = _original_description
        _self.amount = _amount
        _self.transaction_type = _transaction_type
        _self.category = _category
        _self.account = _account
        _self.labels = _labels
        _self.notes = _notes
        _self.instance = _instance

    def is_match( _self, _transaction ):
        is_field_match = True
        is_field_match = is_field_match and ( _self.date == _transaction.date )
        is_field_match = is_field_match and ( _self.description == _transaction.description )
        is_field_match = is_field_match and ( _self.original_description == _transaction.original_description )
        is_field_match = is_field_match and ( _self.amount == _transaction.amount )
        is_field_match = is_field_match and ( _self.transaction_type == _transaction.transaction_type )
        is_field_match = is_field_match and ( _self.category == _transaction.category )
        is_field_match = is_field_match and ( _self.account == _transaction.account )
        is_field_match = is_field_match and ( _self.labels == _transaction.labels )
        is_field_match = is_field_match and ( _self.notes == _transaction.notes )
        return is_field_match

