"""Duel-disk rules with no hardware and no network.

A poll is a card id (or None) plus whether the lever is defense.
Zone turns that into the action byte Godot expects, including the
five-miss removal debounce.
"""

REMOVE_CARD = 0
REMOVE_MISSES = 5


def pack_le(value, length):
    """Unsigned little-endian bytes, `length` long."""
    return bytes((value >> (8 * i)) & 0xFF for i in range(length))


def card_id_from_block(block):
    """16-byte MIFARE block as an integer. The first byte is the least significant.

    ponytail: full 16-byte int, matching the Pi writer. Godot reads the low 16 bits.
    """
    card_id = 0
    for i, byte in enumerate(block):
        card_id += byte * (256 ** i)
    return card_id


def is_defense(level):
    """True when the lever is pressed. NC is tied to GND, so pressed reads 1."""
    return level == 1


def action_id(is_def):
    """1 for face-up attack, 2 for face-up defense."""
    return (1 if is_def else 0) + 1


def action_packet(action, field_id, card_id):
    """32-byte datagram: action u64, field u64, card u128, all little-endian."""
    return pack_le(action, 8) + pack_le(field_id, 8) + pack_le(card_id, 16)


def zone_event(held_id, held_def, card_id, is_def):
    """Action to send for one settled poll, or None.

    held_* is the last state already sent. card_id None means no tag.
    The same id with a flipped lever sends attack or defense again.
    A single miss is not a removal; Zone.poll counts those.
    """
    if card_id is None:
        if held_id is None:
            return None
        return (REMOVE_CARD, held_id)
    if held_id == card_id and held_def == is_def:
        return None
    return (action_id(is_def), card_id)


class Zone:
    """Last packet already sent, and how many polls the tag has been missing."""

    def __init__(self):
        """Start with an empty zone."""
        self.held_id = None
        self.held_def = None
        self.misses = 0

    def poll(self, card_id, is_def):
        """Return (action, card_id) to send, or None.

        card_id None is ignored until REMOVE_MISSES in a row. is_def is
        only used when card_id is not None.
        """
        if self.held_id is not None and card_id is None:
            self.misses += 1
            if self.misses < REMOVE_MISSES:
                return None
        else:
            self.misses = 0
        event = zone_event(self.held_id, self.held_def, card_id, is_def)
        if event is None:
            return None
        action, sent_id = event
        if action == REMOVE_CARD:
            self.held_id = None
            self.held_def = None
        else:
            self.held_id = sent_id
            self.held_def = is_def
        self.misses = 0
        return event


def _self_check():
    """Assert packet layout, lever polarity, and zone polls. No hardware."""
    assert card_id_from_block([0x34, 0x12] + [0] * 14) == 0x1234
    packet = action_packet(1, 2, 0x1234)
    assert len(packet) == 32
    assert packet[0] == 1 and packet[8] == 2
    assert packet[16] == 0x34 and packet[17] == 0x12
    assert action_id(False) == 1 and action_id(True) == 2
    assert is_defense(1) and not is_defense(0)
    assert zone_event(None, None, None, False) is None
    assert zone_event(None, None, 5, False) == (1, 5)
    assert zone_event(5, False, 5, False) is None
    assert zone_event(5, False, 5, True) == (2, 5)
    assert zone_event(5, True, None, True) == (0, 5)
    zone = Zone()
    assert zone.poll(None, None) is None
    assert zone.poll(5, False) == (1, 5)
    assert zone.poll(5, False) is None
    assert zone.poll(5, True) == (2, 5)
    for _ in range(REMOVE_MISSES - 1):
        assert zone.poll(None, None) is None
    assert zone.poll(None, None) == (0, 5)
    assert zone.poll(None, None) is None


if __name__ == "__main__":
    _self_check()
    print("packet check ok")
