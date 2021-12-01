extends Spatial

onready var Card = $Card

func _ready():
	pass

func place_card(card_info, is_facedown, is_attack_pos):
	Card.set_card_info(card_info)
	Card.init_position(is_facedown, is_attack_pos)
	Card.set_visible(true)
	Card.play_animation(is_facedown, is_attack_pos)

func remove_card():
	Card.play_remove_animation()
	Card.wait_for_animation()

func reset():
	Card.set_visible(false)
