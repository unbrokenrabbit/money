
ERROR = 'ERROR'

class Transaction:
    def __init__( _self, _date='', _description='', _amount=0.0, _account='', _instance=0, _bucket='', _bucket_status='' ):
        _self.date = _date
        _self.description = _description
        _self.amount = _amount
        _self.account = _account
        _self.instance = _instance
        _self.bucket = _bucket
        _self.bucket_status = _bucket_status


    def is_match( _self, _transaction ):
        is_field_match = True
        is_field_match = is_field_match and ( _self.date == _transaction.date )
        is_field_match = is_field_match and ( _self.description == _transaction.description )
        is_field_match = is_field_match and ( _self.amount == _transaction.amount )
        is_field_match = is_field_match and ( _self.account == _transaction.account )
        is_field_match = is_field_match and ( _self.instance == _transaction.instance )
        is_field_match = is_field_match and ( _self.bucket == _transaction.bucket )
        is_field_match = is_field_match and ( _self.bucket_status == _transaction.bucket_status )
        return is_field_match

    
    def to_dict( _self ):
        return {
                'account': _self.account,
                'date': _self.date,
                'amount': _self.amount,
                'description': _self.description,
                'instance': _self.instance,
                'bucket': _self.bucket,
                'bucket_status': _self.bucket_status
        }


    def from_dict( _self, _dict ):
        _self.account = _dict[ 'account' ]
        _self.date = _dict[ 'date' ]
        _self.amount = _dict[ 'amount' ]
        _self.description = _dict[ 'description' ]
        _self.instance = _dict[ 'instance' ]
        _self.bucket = _dict[ 'bucket' ]
        _self.bucket_status = _dict[ 'bucket_status' ]


