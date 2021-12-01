from pirc522 import RFID
import RPi.GPIO as GPIO
import time
import socket
from enum import Enum

from write_card_id import BLOCK_NUM, get_num_by_block


class PlayerAction(Enum):
        REMOVE_CARD = 0
        FACEUP_ATTACK = 1
        FACEUP_DEF = 2
        FACEDOWN_ATTACK = 3
        FACEDOWN_DEF = 4


def send_to_godot(sock, action_id, field_id, card_id):
        bytes_action = action_id.to_bytes(8, byteorder="little", signed=False)
        bytes_field = field_id.to_bytes(8, byteorder="little", signed=False)
        bytes_card = card_id.to_bytes(16, byteorder="little", signed=False)
        MESSAGE = bytes_action + bytes_field + bytes_card
        sock.send(MESSAGE)

def get_action_by_flags(is_facedown=False, is_def=False):
        return int(is_facedown) * 2 + int(is_def) + 1

class TagStatus(Enum):
        
        NO_TAG = 0
        TRANSACTION_FAILED = 1
        TRANSACTION_SUCCESS = 2
        IDLE = 3
        REMOVED = 4

def read_tag(reader, util, uid):
        key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
        if not reader.select_tag(uid):
                if not reader.card_auth(reader.auth_a, BLOCK_NUM, key, uid):
                        error, data = reader.read(BLOCK_NUM)
                        card_id = get_num_by_block(data)
                        reader.stop_crypto()
                        if not error:
                                return TagStatus.TRANSACTION_SUCCESS, card_id
        return TagStatus.TRANSACTION_FAILED, None
  
def begin_tag_transaction(reader, util):
        error, tag_type = reader.request()
        if not error:
                dtime = 0
                last_time = time.time()
                error, uid = reader.anticoll()
                if not error:
                        #print("UID: {}".format(uid))
                        status, card_id = read_tag(reader, util, uid)
                        return status, card_id
        
        return TagStatus.TRANSACTION_FAILED, None

def wait_for_tag_remove(reader):
        card_removed = False
        card_removed_counter = 5
        while not card_removed:
            error, tag_type= reader.request()
            if error:
                card_removed_counter = card_removed_counter-1
                if card_removed_counter==0:
                    card_removed = True
            else:
                card_removed_counter = 5

def mfrc_loop(sock, reader, util, ir_pin, field_id=0):
        INITIAL_MESSAGE = b"INITIAL_MESSAGE"
        sock.send(INITIAL_MESSAGE)
        tag_status = TagStatus.NO_TAG
        card_id = 0
        ir_detected = False
        while True:
                while not tag_status == TagStatus.TRANSACTION_SUCCESS:
                        print("Waiting for RFID-Tag...")
                        reader.wait_for_tag()
                        print("RFID-Tag detected")
                        print("Begin Tag transaction...")
                        tag_status, card_id = begin_tag_transaction(reader, util)
                        if tag_status == TagStatus.TRANSACTION_FAILED:
                                print("Transaction failed")
                print("Transaction successful")
                if not bool(GPIO.input(ir_pin)):
                        ir_detected = True
                else:
                        ir_detected = False
                action_id = get_action_by_flags(is_facedown=False, is_def=ir_detected)
                send_to_godot(sock, action_id, field_id, card_id)
                print("Waiting for Tag removal...")
                wait_for_tag_remove(reader)
                print("Tag removed")
                tag_status = TagStatus.REMOVED
                send_to_godot(sock, PlayerAction.REMOVE_CARD.value, field_id, card_id)


def destroy(reader):
        reader.cleanup()
        sock.close()
        #print("Socket closed")

if __name__=="__main__":
        IP = "192.168.178.33"
        PORT = 4242
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect((IP, PORT))
        
        reader = RFID()
        util = reader.util()
        util.debug = True
        
        pin_ir_board = 35
        GPIO.setup(pin_ir_board, GPIO.IN)
        
        try:
                mfrc_loop(sock, reader, util, pin_ir_board)
        except KeyboardInterrupt:
                destroy(reader)
