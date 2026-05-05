# Code & Capture Challenge Writeup: Stringhunt

**Category:** Reverse Engineering  
**Binary:** ELF 64-bit, PIE, stripped, dynamically linked  

---

## Overview

A stripped 64-bit ELF that reads the environment variable `VAULT_KEY`, validates it against a hardcoded secret via XOR obfuscation, and if correct, decodes and prints the flag using the same scheme. Both the expected key and the flag are stored as XOR-0x55 encoded blobs in the `.data` section. As the name hints, `strings` and knowledge of env vars are all you need.

---

## Step 1 — Initial Recon with `strings`

```bash
strings stringhunt
```

Key findings:

```
VAULT_KEY
Access Denied: The vault remains sealed.
.&!'d;2&
#a'&
ded(
```

- **`VAULT_KEY`** — the env var the binary checks.
- **`Access Denied: The vault remains sealed.`** — the only output on failure.
- **`.&!'d;2& / #a'& / ded(`** — printable windows into the XOR-encoded flag blob in `.data`, split by non-printable bytes.

---

## Step 2 — Running the Binary

```bash
./stringhunt
# Access Denied: The vault remains sealed.

VAULT_KEY=test ./stringhunt
# Access Denied: The vault remains sealed.

VAULT_KEY=TOUHATOUHA ./stringhunt
# CodeandCapture{str1ngs_4nd_3nv_v4rs_101}
```

---

## Step 3 — Static Analysis

Three reconstructed functions (binary is stripped):

### `main` (@ `0x129d`)

```c
int main(int argc, char **argv) {
    char *key = getenv("VAULT_KEY");
    if (!check_key(key)) {
        puts("Access Denied: The vault remains sealed.");
        return 1;
    }
    print_flag();
    return 0;
}
```

### `check_key` (@ `0x11a3`)

```asm
; Key comparison loop
11e5:  movzbl (%rax),%eax        ; eax = input[i]
11e8:  xor    $0x55,%eax         ; eax = input[i] ^ 0x55
11eb:  movsbl %al,%edx           ; edx = sign-extended result
...
11f3:  lea    0x2e54(%rip),%rcx  ; rcx = &stored_key (VA 0x4058)
11fa:  movzbl (%rax,%rcx,1),%eax ; eax = stored_key[i]
1201:  cmp    %eax,%edx          ; (input[i] ^ 0x55) == stored_key[i] ?
1203:  je     120c               ; match → keep looping
1205:  mov    $0x0,%eax          ; mismatch → return 0
```

Reconstructed C:

```c
int check_key(char *input) {
    if (!input || strlen(input) != 10)
        return 0;
    for (int i = 0; i <= 9; i++) {
        if ((input[i] ^ 0x55) != stored_key[i])   // stored_key @ VA 0x4068
            return 0;
    }
    return 1;
}
```

Check condition: `input[i] ^ 0x55 == stored_key[i]`  
→ correct key byte: `input[i] = stored_key[i] ^ 0x55`

### `print_flag` (@ `0x121d`)

```c
void print_flag() {
    char buf[64];
    for (int i = 0; i <= 0x27; i++)         // 40 bytes
        buf[i] = flag_encoded[i] ^ 0x55;    // flag_encoded @ VA 0x4030
    buf[40] = '\0';
    puts(buf);
    bzero_buf(buf, 0x28);                   // wipe flag from memory after printing
}
```

Same XOR scheme — flag is stored obfuscated and decoded at runtime with `^ 0x55`.

---

## Step 4 — Locating the Data

Both blobs live in `.data` (file offset `0x3020`, VA `0x4020`):

```
VA 0x4030  (file 0x3030) — 40 bytes — XOR-encoded flag
VA 0x4058  (file 0x3068) — 10 bytes — XOR-encoded key
```

Hex dump of `.data`:

```
4020: 00 00 00 00 00 00 00 00 28 40 00 00 00 00 00 00   ........(@......
4030: 13 19 14 12 2e 26 21 27 64 3b 32 26 0a 61 3b 31   .....&!'d;2&.a;1
4040: 0a 66 3b 23 0a 23 61 27 26 0a 64 65 64 28 14 10   .f;#.#a'&.ded(..
4050: 01 1d 10 07 <flag_end>  <key_bytes_10...>
```

The fragments `.&!'d;2&`, `#a'&`, `ded(` that `strings` surfaced are the printable runs inside the flag blob at `0x4030`, split by non-printable bytes — breadcrumbs pointing straight at the obfuscated data.

---

## Step 5 — Decoding Key and Flag

XOR is self-inverse: `x ^ k ^ k = x`. Decoding is the same operation as encoding.

```python
data = open("stringhunt", "rb").read()

key_enc  = data[0x3068 : 0x3068 + 10]
flag_enc = data[0x3030 : 0x3030 + 40]

key  = bytes(b ^ 0x55 for b in key_enc)
flag = bytes(b ^ 0x55 for b in flag_enc)

print("Key :", key.decode())    # TOUHATOUHA
print("Flag:", flag.decode())   # CodeandCapture{str1ngs_4nd_3nv_v4rs_101}
```

Verification — `TOUHATOUHA ^ 0x55` matches the stored key bytes exactly.

---

## Summary

| Item | Value |
|------|-------|
| Trigger | `VAULT_KEY` environment variable |
| Key validation | `input[i] ^ 0x55 == stored_key[i]`, length must be **10** |
| Correct key | `TOUHATOUHA` |
| Flag encoding | XOR 0x55, 40 bytes at file offset `0x3030` |
| **Flag** | **`CodeandCapture{str1ngs_4nd_3nv_v4rs_101}`** |

### Key Takeaways

1. **Challenge name is the hint** — *stringhunt* tells you to run `strings`. The env var name `VAULT_KEY` and the encoded blob's printable fragments surface immediately.
2. **XOR with a constant is trivially reversible** — the same `^ 0x55` that encodes also decodes; no key cracking needed.
3. **`TOUHATOUHA ^ 0x55` lands entirely below `0x20`** — all stored key bytes are non-printable control characters, making the key invisible to `strings` but trivially recovered with one XOR pass.
4. **`bzero_buf` after printing** wipes the decoded flag from the stack as a runtime anti-forensics measure — irrelevant to static analysis.
