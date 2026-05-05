data = open("stringhunt", "rb").read()

key_enc  = data[0x3068 : 0x3068 + 10]
flag_enc = data[0x3040 : 0x3040 + 40]

key  = bytes(b ^ 0x55 for b in key_enc)
flag = bytes(b ^ 0x55 for b in flag_enc)

print("Key :", key.decode())    # TOUHATOUHA
print("Flag:", flag.decode())   # CodeandCapture{str1ngs_4nd_3nv_v4rs_101}