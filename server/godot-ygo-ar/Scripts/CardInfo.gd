extends Resource
class_name CardInfo

enum CardType{
	MONSTER = 0,
	SPELL = 1,
	TRAP = 2
}

export(String) var card_name
export(Texture) var card_image
export(CardType) var card_type
export(int) var card_monster_stars
export(int) var card_monster_atk
export(int) var card_monster_def
