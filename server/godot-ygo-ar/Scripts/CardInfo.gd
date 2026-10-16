extends Resource
class_name CardInfo

enum CardType{
	MONSTER = 0,
	SPELL = 1,
	TRAP = 2
}

@export var card_name: String
@export var card_image: Texture2D
@export var card_type: CardType
@export var card_monster_stars: int
@export var card_monster_atk: int
@export var card_monster_def: int
