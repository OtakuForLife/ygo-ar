extends Control

signal on_player_action(player_id, action_id, field_id, card_id)
signal clear_all

var CardDatabase = null

var player_id = 0
var action_id = 0
var field_id = 0
var card_id = 0

@onready var CardOptions = $MarginContainer2/MarginContainer/HBoxContainer/Cards
@onready var PlayerOption = $MarginContainer2/MarginContainer/HBoxContainer/Player
@onready var Fields = $MarginContainer2/MarginContainer/HBoxContainer/Fields
@onready var Action = $MarginContainer2/MarginContainer/HBoxContainer/Action

func _ready():
	PlayerOption.add_item("Player 1")
	PlayerOption.add_item("Player 2")
	
	var fields = ["Monster 1", "Monster 2", "Monster 3", "Monster 4", "Monster 5", "SpellTrap 1", "SpellTrap 2", "SpellTrap 3", "SpellTrap 4", "SpellTrap 5"]
	for n in fields:
		Fields.add_item(n)
	
	# action_id:
	# 0 ... remove
	# 1 ... faceup attack
	# 2 ... faceup def
	# 3 ... facedown attack
	# 4 ... facedown def
	Action.add_item("Remove")
	Action.add_item("Faceup Attack")
	Action.add_item("Faceup Defense")
	Action.add_item("Facedown Attack")
	Action.add_item("Facedown Defense")


func _on_Button_pressed():
	emit_signal("on_player_action", player_id, action_id, field_id, card_id)


func _on_Main_init(database):
	CardDatabase = database
	CardOptions.clear()
	for card in database.get_card_resources():
		CardOptions.add_item(card.card_name)

func _on_Player_item_selected(index):
	player_id = index

func _on_Fields_item_selected(index):
	field_id = index

func _on_OptionButton_item_selected(index):
	card_id = index

func _on_Action_item_selected(index):
	action_id = index


func _on_Clear_pressed():
	emit_signal("clear_all")
