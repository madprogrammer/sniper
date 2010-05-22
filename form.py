from formencode import Schema, validators

class ItemForm(Schema):
	id = validators.Int()
	maxbid = validators.Number()

