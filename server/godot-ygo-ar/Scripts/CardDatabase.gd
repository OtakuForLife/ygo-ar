extends Resource
class_name CardDatabase

@export var card_resources: Array[Resource] = []

func _ready():
	pass

func get_card_by_id(id):
	return card_resources[id]

func get_card_resources():
	return card_resources
