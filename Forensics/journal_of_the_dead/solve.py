names = [
         b"T3mP_Fl4g_X0r_C0mbin3d.txt",
         b"l0g_f1n4l_v3rs10n_b4ck.bin",
         b"dump_snapshot_042_vx00.cfg",
         b"tmp_fin4l_4rch1ve_v002.dat",
         b"3B8874ZCwzr2NiCB2K7xp0uNPM",
         b"qiZjYm4IP0_X1AodUBX5SMFk-7",
        ]

result = bytearray(26)
for name in names:
    for i in range(26):
        result[i] ^= name[i]

print(result.decode())
# j0urn4l_0f_th3_d34d_sp34ks