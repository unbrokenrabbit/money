class Bucket:
    def __init__( _self, _id='', _name='', _pattern='', _account='', _direction='' ):
        _self.id = _id
        _self.name = _name
        _self.pattern = _pattern
        _self.account = _account
        _self.direction = _direction


    def to_dict( _self ):
        return {
            'id': _self.id,
            'name': _self.name,
            'pattern': _self.pattern,
            'account': _self.account,
            'direction': _self.direction
        }


    def from_dict( _self, _dict ):
        _self.id = _dict[ 'id' ]
        _self.name = _dict[ 'name' ]
        _self.pattern = _dict[ 'pattern' ]
        _self.account = _dict[ 'account' ]
        _self.direction = _dict[ 'direction' ]


