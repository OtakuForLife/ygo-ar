# ygo-ar

A Yu-Gi-Oh duel disk worn on the arm. A card placed on a zone appears on the Godot field, and the lever sets attack or defense.

The disk is the printed shell in `hardware/` (current design v2.3), with a deck and graveyard that stay put while the arm moves. An ESP32 inside it reads the card id from a MIFARE block with an RC522 and the lever with an SS-5GL switch. `client/esp32/` sends that over UDP. `server/godot-ygo-ar/` (Godot 4.6) shows the card on the field. `server/yugioh-ar-(3.x)/` is the older Godot 3 version of the same view.

A newly placed card is summoned. The same card changes position when the lever flips. Removing it clears the zone.

## Vision

The duel from the show, played with a disk on your arm and seen in the room. Each duelist wears a disk. Physical cards on the monster and spell zones drive one shared field, and the summon stands in space through the XR camera in Godot. Stance is the lever under the card, not a menu. Deck and graveyard stay on the disk, so the whole duel is the object on your arm.
