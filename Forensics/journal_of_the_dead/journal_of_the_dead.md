# Code & Capture 1.0 Challenge Writeup: Journal of the Dead

**Category:** Digital Forensics / File System Analysis  
**Difficulty:** Medium-Hard  
**File:** `suspect_sd.img` (ext4 image, ~200 MB)

---

## Provided File

- `suspect_sd.img`

---

## Technical Details

The image was created with the following steps:

- A secret file `/secret.txt` was created.
- It was **renamed six times** in quick succession:
  - `T3mP_Fl4g_X0r_C0mbin3d.txt`
  - `l0g_f1n4l_v3rs10n_b4ck.bin`
  - `dump_snapshot_042_vx00.cfg`
  - `tmp_fin4l_4rch1ve_v002.dat`
  - `3B8874ZCwzr2NiCB2K7xp0uNPM`
  - `qiZjYm4IP0_X1AodUBX5SMFk-7`
  - (These exact names appear in the journal.)
- The file was then deleted and the same inode reused for `/innocent.jpg` filled with random data.
- The filesystem journal records every directory metadata operation as a sequence of committed transactions.
- The journal is left in a dirty state, leaving the transaction history intact inside the image.

All six historical filenames are still present inside the journal's directory entry structures. The **XOR of all six filenames** (raw bytes, all exactly 26 bytes long) reveals the flag content.

---

## Intended Solution

### 1. Confirm the journal is present and active

```bash
debugfs -R "logdump -S" suspect_sd.img
```

You will see output like:

```
Journal sequence: 0x00000001
Journal start:    1
Total journal blocks: 4096
...
Journal starts at block 1, transaction 1
Found expected sequence 1, type 1 (descriptor block) at block 1
  FS block 3230 logged at journal block 2 (flags 0x8)
Found expected sequence 1, type 2 (commit block) at block 3
...
```

Seven transactions exist, each journaling the same filesystem block (the root directory).

### 2. Locate the six filenames in the journal

Use the `-b` flag to find every journal snapshot of the root directory block:

```bash
debugfs -R "logdump -b 3230" suspect_sd.img
```

*(Replace `3230` with the actual root directory block number shown in the `logdump` output.)*

Then extract the raw journal data blocks and parse the directory entries. A quick method using `strings`:

```bash
strings suspect_sd.img | grep -E '^[A-Za-z0-9._-]{26}$'
```

You will see all six 26-byte names. Alternatively, use `hexdump` or a Python script to parse the `ext4_dir_entry_2` structures directly from the journal data blocks.

### 3. XOR the names

All six names are exactly 26 bytes. XOR them byte-by-byte:

```python
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
```

### 4. Flag

```
CodeandCapture{j0urn4l_0f_th3_d34d_sp34ks}
```
