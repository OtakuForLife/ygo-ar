extends XROrigin3D

@export var debug: bool = true

const DEBUG_MOUSE_SENSETIVITY = 0.2
const DEBUG_MOVEMENT_SPEED = 0.2

@onready var camera: XRCamera3D = $XRCamera3D

func _ready():
	if debug:
		Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)


func _input(event):
	if debug:
		if event is InputEventMouseMotion and Input.get_mouse_mode() == Input.MOUSE_MODE_CAPTURED:
			var movement = event.relative
			camera.rotation.x += -deg_to_rad(movement.y * DEBUG_MOUSE_SENSETIVITY)
			camera.rotation.y += -deg_to_rad(movement.x * DEBUG_MOUSE_SENSETIVITY)
	

func _process(_delta):
	if debug:
		var cam_xform = camera.get_global_transform()
		var move_axis = Vector3()
		var input_axis = Vector3()
		input_axis.y = int(Input.is_action_pressed("cam_down")) - int(Input.is_action_pressed("cam_up"))
		input_axis.x = int(Input.is_action_pressed("cam_right")) - int(Input.is_action_pressed("cam_left"))
		input_axis.z = int(Input.is_action_pressed("move_up"))
		input_axis = input_axis.normalized()
		move_axis += cam_xform.basis.z * input_axis.y
		move_axis += cam_xform.basis.x * input_axis.x
		move_axis.y += input_axis.z
		global_position += move_axis.normalized() * DEBUG_MOVEMENT_SPEED
		if Input.is_action_just_pressed("ui_cancel"):
			if Input.get_mouse_mode() == Input.MOUSE_MODE_CAPTURED:
				Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
			else:
				Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)
