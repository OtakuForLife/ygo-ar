extends Node3D

@onready var default_field = $Monster/Field3

@onready var fields = [$Monster/Field1, $Monster/Field2, $Monster/Field3, $Monster/Field4, $Monster/Field5, 
						$SpellTrap/Field1, $SpellTrap/Field2, $SpellTrap/Field3, $SpellTrap/Field4, $SpellTrap/Field5]

func _ready():
	pass

func place_card_on_field(field_id, card_info, is_facedown, is_attack_pos):
	var field = default_field
	if field_id >=0 and field_id < len(fields):
		field = fields[field_id]
	field.place_card(card_info, is_facedown, is_attack_pos)

func remove_card(field_id):
	if field_id >=0 and field_id < len(fields):
		fields[field_id].remove_card()


func clear_all():
	for f in fields:
		f.reset()
