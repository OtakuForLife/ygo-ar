extends Resource
class_name CardDatabase

export(Array, Resource) var card_resources = []

func _ready():
	pass

func get_card_by_id(id):
	return card_resources[id]

func get_card_resources():
	return card_resources
