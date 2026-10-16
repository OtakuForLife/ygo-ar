@tool
extends Node3D

@export var card_info: Resource

@onready var Images = $Images
@onready var front_sprite = $Images/Front
@onready var back_sprite = $Images/Background
@onready var anim_player = $AnimationPlayer

func _ready():
	front_sprite.texture = card_info.card_image

func set_card_info(new_card_info):
	card_info = new_card_info
	front_sprite.texture = card_info.card_image


func init_position(is_facedown, is_attack_pos):
	if is_facedown:
		Images.rotation_degrees.y = 0
	else:
		Images.rotation_degrees.y = 180
	
	if is_attack_pos:
		Images.rotation_degrees.z = 0
	else:
		Images.rotation_degrees.z = 270

func play_animation(is_facedown, is_attack_pos):
	front_sprite.modulate.a = 1.0
	back_sprite.modulate.a = 1.0
	var is_monster = card_info.card_type == CardInfo.CardType.MONSTER
	if is_monster and !is_facedown and is_attack_pos:
		anim_player.play("ActivateMonsterAttack")
	elif is_monster and !is_facedown and !is_attack_pos:
		anim_player.play("ActivateMonsterDef")
	elif is_monster and is_facedown and !is_attack_pos:
		anim_player.play("SetMonsterDef")
	elif !is_monster and !is_facedown:
		anim_player.play("ActivateSpellTrap")
	else:
		anim_player.play("SetSpellTrap")

func wait_for_animation():
	await anim_player.animation_finished


func play_remove_animation():
	anim_player.play("Remove")

func play_show_animation():
	anim_player.play("Show")
