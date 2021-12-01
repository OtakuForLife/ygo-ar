extends Spatial

signal init(database)

var card_database = preload("res://Resources/CardDatabase.tres")

onready var player1_field = $Field/Player1
onready var player2_field = $Field/Player2

const DEFAULT_CARD = preload("res://Resources/Monster/Monster_Kuriboh.tres")

func _ready():
	emit_signal("init", card_database)


# warning-ignore:unused_argument
func _on_player_action_received(player_id: int, action_id: int, field_id: int, card_id: int):
	var player_side = player1_field
	if player_id == 1:
		player_side = player2_field
		
	var card = DEFAULT_CARD
	if card_id >= 0 and card_id < card_database.card_resources.size():
		card = card_database.card_resources[card_id]
	
	# action_id:
	# 0 ... remove
	# 1 ... faceup attack
	# 2 ... faceup def
	# 3 ... facedown attack
	# 4 ... facedown def
	var is_attack = (action_id % 2 == 1)
	var is_face_down = float(action_id) / 2 > 1
	
	if action_id == 0:
		player_side.remove_card(field_id)
	else:
		player_side.place_card_on_field(field_id, card, is_face_down, is_attack)


func _on_TestUI_clear_all():
	player1_field.clear_all()
	player2_field.clear_all()
