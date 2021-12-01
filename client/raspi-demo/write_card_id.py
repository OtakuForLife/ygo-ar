# -*- coding: utf-8 -*-
BLOCK_NUM = 10

def get_num_by_block(block):
        data_int = 0
        for i in range(0, len(block)):
                data_int += block[i] * (256**i)
        return data_int

if __name__=="__main__":
        from pirc522 import RFID

        rdr = RFID()
        util = rdr.util()
        # Set util debug to true - it will print what's going on
        util.debug = True

        # Wait for tag
        print("put your RFID Tag over the reader!")
        rdr.wait_for_tag()
        # Request tag
        (error, data) = rdr.request()
        if not error:
            (error, uid) = rdr.anticoll()
            if not error:
                util.set_tag(uid)
                util.auth(rdr.auth_a, [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
                
                card_id = input("Number to write: ")
                card_id = int(card_id)
                id_bytes = bytearray(card_id.to_bytes(16, byteorder="little", signed=False))
                util.do_auth(BLOCK_NUM)
                rdr.write(BLOCK_NUM, id_bytes)
                
                
                print("Reading again: ")
                #util.read_out(BLOCK_NUM)
                num_read = rdr.read(BLOCK_NUM)[1]
                data_int = get_num_by_block(num_read)
                print("Number {} could be read on Block {}".format(data_int, BLOCK_NUM))
                        
                        
                util.deauth()
        rdr.cleanup()
