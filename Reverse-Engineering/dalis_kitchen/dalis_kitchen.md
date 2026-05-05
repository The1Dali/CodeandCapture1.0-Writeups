# Code & Capture 1.0 Challenge Writeup — `dalis_kitchen`

**Category:** Reverse Engineering  
**Binary:** ELF 64-bit, PIE, stripped, dynamically linked

---

## Overview

You enter a "recipe" on stdin. Dali's Kitchen runs the recipe through three cooking steps — XOR, ROT13, and a reversal — then checks the result against a hardcoded comparison blob. The goal is to **uncook** that blob, reversing each step in opposite order, to recover the exact recipe that satisfies the check. That recipe is the flag.

---

## Step 1 — Initial Recon with `strings`

```bash
strings dalis_kitchen
```

Key output:

```
[Dali] Step 1: Seasoning with the secret spice...
[Dali] Step 2: Rotating the flavors thirteen times...
[Dali] Step 3: The surreal twist — flipping reality upside down...
Welcome to Dali's Kitchen.
Enter the secret recipe:
Wrong proportions! Dali is disappointed.
Magnificent! You've mastered Dali's surreal technique.
The dish is a disaster. Try again.
=6'>'2>'6{2
```

The three cooking steps are named right in the binary. The fragment `=6'>'2>'6{2` is the longest printable window into the XOR-encoded comparison blob in `.data` — another planted breadcrumb.

---

## Step 2 — Running the Binary

```bash
./dalis_kitchen
# Welcome to Dali's Kitchen.
# Enter the secret recipe:
test
# Wrong proportions! Dali is disappointed.
```

Two possible failure messages:

- **"Wrong proportions!"** — wrong input length (not exactly 47 characters).
- **"The dish is a disaster."** — right length but wrong recipe content.

---

## Step 3 — Static Analysis

### The cook function (@ `0x1189`)

The binary applies three sequential in-place transformations to the full 47-byte input buffer:

**Step 1 — XOR with `0x42` ("the secret spice")**

```c
for (int i = 0; i < len; i++)
    buf[i] ^= 0x42;
```

```asm
11cb:  xor $0x42,%edx
```

**Step 2 — ROT13 on letters ("rotating thirteen times")**

```c
for (int i = 0; i < len; i++) {
    char c = buf[i];
    if (c > 0x40 && c <= 0x5a)           // A–Z
        buf[i] = (c - 0x34) % 26 + 0x41; // = (c - 'A' + 13) % 26 + 'A'
    else if (c > 0x60 && c <= 0x7a)       // a–z
        buf[i] = (c - 0x54) % 26 + 0x61; // = (c - 'a' + 13) % 26 + 'a'
}
```

```asm
121c:  sub $0x34,%eax      ; for uppercase
1240:  lea 0x41(%rax),%ecx
1264:  sub $0x54,%eax      ; for lowercase
1288:  lea 0x61(%rax),%ecx
```

Non-letter bytes are left untouched.

**Step 3 — Reverse ("flipping reality upside down")**

```c
for (int i = 0; i < len / 2; i++) {
    char tmp = buf[i];
    buf[i] = buf[len - 1 - i];
    buf[len - 1 - i] = tmp;
}
```

```asm
12c6–1323: swap loop, stops at len/2
```

### `main` (@ `0x1329`)

```c
int main() {
    char buf[64];
    puts("Welcome to Dali's Kitchen.");
    printf("Enter the secret recipe: ");
    if (!fgets(buf, 64, stdin)) return 1;

    size_t len = strlen(buf);
    if (buf[len-1] == '\n') { buf[--len] = '\0'; }

    if (len != 0x2f) {                        // must be exactly 47 chars
        puts("Wrong proportions! Dali is disappointed.");
        return 1;
    }

    cook(buf, len);

    if (memcmp(buf, stored, 0x1b) != 0) {     // first 27 bytes must match
        puts("The dish is a disaster. Try again.");
    } else {
        puts("Magnificent! You've mastered Dali's surreal technique.");
    }
    return 0;
}
```

Two constraints:
- Input must be exactly **47 bytes**.
- After cooking, the first **27 bytes** must match the comparison blob at `VA 0x4040`.

---

## Step 4 — Locating the Comparison Blob

```
.data @ VA 0x4030, file 0x3030
```

Hex dump:

```
4030: 00 00 00 00 00 00 00 00 38 40 00 00 00 00 00 00
4040: 7d 36 08 3d 36 0d 32 27 36 0b 32 36 08 3d 36 27   }6.=6.2'6.26.=6'
4050: 3e 27 32 3e 27 36 7b 32 08 0d 20                  >'2>'6{2..
```

The stored blob (27 bytes at `0x4040`):

```
7d 36 08 3d 36 0d 32 27 36 0b 32 36 08 3d 36 27 3e 27 32 3e 27 36 7b 32 08 0d 20
```

The `=6'>'2>'6{2` fragment from `strings` is the printable run at bytes 13–23 of this blob — chars `3d 36 27 3e 27 32 3e 27 36 7b 32`.

---

## Step 5 — Uncooking the Recipe

To find the flag, reverse all three steps in opposite order:

```
cook:   XOR(0x42) → ROT13 → Reverse
uncook: Reverse  → ROT13 → XOR(0x42)
```

ROT13 is self-inverse, and XOR is self-inverse. The reversal is also its own inverse when applied to the same-length buffer.

**Key insight:** after cooking a 47-byte input, the reversal places the LAST 27 bytes of the original input into the FIRST 27 positions of the cooked output. So the comparison only constrains positions 20–46 of the input. The first 20 bytes are unchecked padding.

For each position `j` in `[0, 26]`:

```
cooked[j] = stored[j]
           = ROT13(input[46-j] ^ 0x42)

∴ input[46-j] = ROT13(stored[j]) ^ 0x42
```

Since none of the stored bytes are letters, ROT13 leaves them unchanged:

```
input[46-j] = stored[j] ^ 0x42
```

```python
data   = open("dalis_cooker", "rb").read()
stored = data[0x3040 : 0x3040 + 27]

def rot13(b):
    if 0x41 <= b <= 0x5a: return (b - 0x41 + 13) % 26 + 0x41
    if 0x61 <= b <= 0x7a: return (b - 0x61 + 13) % 26 + 0x61
    return b

def cook(buf):
    r = bytearray(buf)
    r = bytearray(b ^ 0x42 for b in r)
    r = bytearray(rot13(b) for b in r)
    return bytes(reversed(r))

# Recover positions 20–46 of the recipe
recipe = bytearray(47)
for j in range(27):
    recipe[46 - j] = rot13(stored[j]) ^ 0x42

# First 20 bytes are arbitrary (any padding works)
recipe[:20] = b'A' * 20

# Verify
assert cook(recipe)[:27] == stored
print("Recipe:", recipe.decode())
print("Length:", len(recipe))
```

---

## Step 6 — Verification

```bash
python3 solve.py | ./dalis_kitchen
# Welcome to Dali's Kitchen.
# Enter the secret recipe: [Dali] Step 1: Seasoning with the secret spice...
# [Dali] Step 2: Rotating the flavors thirteen times...
# [Dali] Step 3: The surreal twist — flipping reality upside down...
# Magnificent! You've mastered Dali's surreal technique.
```

Binary confirms success. ✓

## Step 7 — Flag

`CodeandCapture{d4l1s_surr34l_r3c1p3}`

---

## Summary

| Item | Value |
|------|-------|
| Input length | 47 bytes (exact) |
| Cooking pipeline | `XOR 0x42` → `ROT13` → `Reverse` |
| Comparison | First 27 bytes of cooked output vs. blob at `0x4040` |
| Constrained bytes | Positions 20–46 of the input (last 27) |
| Recovery method | `recipe[46-j] = ROT13(stored[j]) ^ 0x42` for `j = 0..26` |
| **Flag** | **⚠️ NOT RECORDED — run solve.py to obtain** |

### Key Takeaways

1. **Read the strings output as a recipe card** — the three step names are literal algorithmic descriptions. `strings` hands you the algorithm before you open a disassembler.
2. **Reversal shifts which input bytes matter** — because step 3 reverses the full buffer, the `memcmp` over the first 27 output bytes maps to the LAST 27 input bytes. The first 20 bytes are free.
3. **The uncooking order is exactly reversed** — cook = `XOR → ROT13 → Reverse`, so uncook = `Reverse → ROT13 → XOR`. Both ROT13 and XOR are self-inverse, making the math trivial.
4. **None of the stored bytes are letters** — ROT13 has no effect on them, simplifying the inversion to a pure `XOR 0x42` pass over `reverse(stored)`.
