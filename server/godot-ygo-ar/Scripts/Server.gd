extends Node

signal on_player_action(player_id, action_id, field_id, card_id)

var server := UDPServer.new()
var peers = []

func _ready():
	print("Server starting...")
	server.listen(4242)

func _process(delta):
	server.poll() # Important!
	if server.is_connection_available():
		var peer : PacketPeerUDP = server.take_connection()
		var pkt = peer.get_packet()
		print("Accepted peer: %s:%s" % [peer.get_packet_ip(), peer.get_packet_port()])
		print("Received data: %s" % [pkt.get_string_from_utf8()])
		# Reply so it knows we received the message.
		#peer.put_packet(pkt)
		# Keep a reference so we can keep contacting the remote peer.
		peers.append(peer)
	
	for pid in range(0, peers.size()):
		var peer = peers[pid]
		var msg: PoolByteArray = peer.get_packet()
		if not msg.empty():
			process_package(pid, msg)

func process_package(player_id, package):
	print("##########################")
	print("Packet Size: "+str(package.size()))
	var buffer = StreamPeerBuffer.new()
	
	var action_bits = package.subarray(0, 7)
	buffer.set_data_array(action_bits)
	var action_id = buffer.get_u8()
	
	var field_bits = package.subarray(8, 15)
	buffer = StreamPeerBuffer.new()
	buffer.set_data_array(field_bits)
	var field_id = buffer.get_u8()
	
	var card_bits = package.subarray(16, 31)
	buffer = StreamPeerBuffer.new()
	buffer.set_data_array(card_bits)
	var card_id = buffer.get_u16()
	print("--------Packet Info--------")
	print("Player ID: "+str(player_id))
	print("Action: "+str(action_id))
	print("Field: "+str(field_id))
	print("Card ID: "+str(card_id))
	
	emit_signal("on_player_action", player_id, action_id, field_id, card_id)
