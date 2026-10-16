"""ESP32 MicroPython client for one duel-disk zone.

Reads a card id from an RC522 and attack/defense from an SS-5GL-CB1325,
then sends the same 32-byte UDP packet as client/raspi-demo/ygo_dueldisk_client.py.
The card block is written by client/raspi-demo/write_card_id.py.

mfrc522.py is the chip driver. zone.py decides which packet to send.
This file wires the pins, joins WiFi, and polls.

Wiring on an ESP32 DevKit with a CP2102 USB-UART. Power the RC522 from 3V3.

    RC522 3.3V                          3V3
    RC522 GND                           GND
    RC522 SDA (chip select)             GPIO 5
    RC522 SCK                           GPIO 18
    RC522 MOSI                          GPIO 23
    RC522 MISO                          GPIO 19
    RC522 RST                           GPIO 22
    RC522 IRQ                           unconnected
    SS-5GL pin 2 (C, left, lever up)    GPIO 4, internal pull-up
    SS-5GL pin 1 (NC, right)            GND
    SS-5GL pin 3 (NO, middle)           unconnected

The middle lug is left open. Lever released keeps C tied to NC, so GPIO 4
is low and the card is attack. Lever pressed opens NC, the pull-up makes
GPIO 4 high, and the card is defense.

Packet, little-endian, 32 bytes:

    offset 0   action   u64    0 remove, 1 face-up attack, 2 face-up defense
    offset 8   field    u64    FIELD_ID
    offset 16  card     u128   MIFARE block BLOCK_NUM; Godot uses the low 16 bits

A card sends action 1 or 2 when it appears, and again when the lever flips
while that same id is still on the reader. Five missed polls send action 0.
Facedown actions 3 and 4 exist on the Pi client and are unused here.
Godot's UDPServer uses the first datagram only to register the peer, so
main() sends b"INITIAL_MESSAGE" before any action packet.

The board needs MicroPython ESP32_GENERIC and a COM port from the
Silicon Labs CP210x driver. From this directory:

    pip install mpremote
    python -m mpremote connect COMx cp main.py mfrc522.py zone.py :
    python -m mpremote connect COMx reset

On a PC, where the machine module is missing, running this file only
executes the zone self-check.
"""

from zone import REMOVE_CARD, Zone, action_packet, card_id_from_block, is_defense, _self_check

WIFI_SSID = "Fuujin"
WIFI_PASSWORD = "9goijC9DrDUbC*sQEue@FR$fc`c3d<"
GODOT_IP = "192.168.178.23"
GODOT_PORT = 4242
FIELD_ID = 0

PIN_SCK = 18
PIN_MOSI = 23
PIN_MISO = 19
PIN_CS = 5
PIN_RST = 22
PIN_SW = 4

BLOCK_NUM = 10
KEY_A = b"\xff\xff\xff\xff\xff\xff"

try:
    from machine import Pin, SPI
    import network
    import time
    from mfrc522 import MFRC522
except ImportError:
    Pin = SPI = network = time = MFRC522 = None


def read_card_id(reader):
    """Card id from BLOCK_NUM, or None when no tag is present or auth fails."""
    if reader.request() != reader.OK:
        return None
    stat, uid = reader.anticoll()
    if stat != reader.OK:
        return None
    if reader.select(uid) != reader.OK:
        return None
    if reader.auth(BLOCK_NUM, KEY_A, uid) != reader.OK:
        return None
    block = reader.read_block(BLOCK_NUM)
    reader.stop_crypto()
    if block is None:
        return None
    return card_id_from_block(block)


def connect_wifi():
    """Join WIFI_SSID. Raise RuntimeError if the association times out."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("WiFi", WIFI_SSID)
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        for _ in range(40):
            if wlan.isconnected():
                break
            time.sleep_ms(250)
    if not wlan.isconnected():
        raise RuntimeError("WiFi failed")
    print("IP", wlan.ifconfig()[0])
    return wlan


def open_reader():
    """SPI RC522 on the pins above. Raise if VersionReg is not a chip."""
    spi = SPI(1, baudrate=1_000_000, polarity=0, phase=0,
              sck=Pin(PIN_SCK), mosi=Pin(PIN_MOSI), miso=Pin(PIN_MISO))
    reader = MFRC522(spi, Pin(PIN_CS), Pin(PIN_RST))
    version = reader.version()
    print("RC522 version", hex(version))
    if version in (0x00, 0xFF):
        raise RuntimeError("RC522 not found, check wiring and 3.3 V")
    return reader


def main():
    """Announce this board, then send whatever Zone.poll reports."""
    _self_check()
    connect_wifi()
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((GODOT_IP, GODOT_PORT))
    # Godot's UDPServer consumes the first packet to register the peer.
    sock.send(b"INITIAL_MESSAGE")

    reader = open_reader()
    lever = Pin(PIN_SW, Pin.IN, Pin.PULL_UP)
    zone = Zone()
    while True:
        card_id = read_card_id(reader)
        is_def = is_defense(lever.value()) if card_id is not None else None
        event = zone.poll(card_id, is_def)
        if event is not None:
            action, sent_id = event
            if action == REMOVE_CARD:
                print("removed", sent_id)
            else:
                print("card", sent_id, "def" if is_def else "atk")
            sock.send(action_packet(action, FIELD_ID, sent_id))
        time.sleep_ms(50)


if __name__ == "__main__":
    if Pin is None:
        _self_check()
        print("packet check ok")
    else:
        main()
