# Code & Capture 1.0 Challenge Writeups

Official writeups for Code & Capture 1.0 challenges. Each folder contains a full walkthrough — recon, static analysis, solve script, and flag — written to be self-contained and reproducible.

---

## Challenges

| # | Challenge | Category | Difficulty | Flag |
|---|-----------|----------|------------|------|
| 1 | [stringhunt](./Reverse-Engineering/stringhunt/) | Reverse Engineering | Easy | `CodeandCapture{str1ngs_4nd_3nv_v4rs_101}` |
| 2 | [dalis_kitchen](./Reverse-Engineering/dalis_kitchen/) | Reverse Engineering | Medium | `CodeandCapture{d4l1s_surr34l_r3c1p3}` |
| 3 | [journal_of_the_dead](./Forensics/journal_of_the_dead/) | Digital Forensics | Medium-Hard | `CodeandCapture{j0urn4l_0f_th3_d34d_sp34ks}` |
| 4 | [noise_hunt](./Forensics/noise_hunt/) | Forensics / Linux CLI | Easy-Medium | `CodeandCapture{you_mastered_grep_and_regex_in_this_ctf_challenge_d4t4_h1d1ng_7f3a2b}` |
| 5 | [phase_phantom](./Forensics/phase_phantom/) | Forensics / Audio Steganography | Medium | `CodeandCapture{ph4s3_inv3rs10n_r3v34ls_4ll}` |

---

## Repository Structure

```
CodeandCapture1.0-Writeups/
│
├── README.md
│
├── Reverse-Engineering/
│   ├── stringhunt/
│   │   ├── README.md                   # Full writeup
│   │   ├── solve.py                    # Decode key + flag from binary
│   │   └── stringhunt                  # Target Binary
│   │
│   └── dalis_kitchen/
│       ├── README.md                   # Full writeup
│       ├── solve.py                    # Uncook the comparison blob, recover recipe
│       └── dalis_cooker                # Target binary
│
└── Forensics/
    ├── journal_of_the_dead/
    │   ├── README.md                   # Full writeup
    │   ├── solve.py                    # Extract filenames from journal, XOR to flag
    │   └── suspect_sd_card.img         # Target SD card image
    │
    ├── noise_hunt/
    │   ├── README.md                   # Full writeup (solution is a one-liner grep)
    │   └── haystack.zip                # Zipped folder with the scattered flags
    │
    └── phase_phantom/
        ├── README.md                   # Full writeup
        ├── solve.py                    # L-R channel subtraction, outputs flag.wav
        └── whistleblower_memo.wav      # Target .wav file
```

---

## Tools Referenced

| Tool | Used In |
|------|---------|
| `strings`, `hexdump`, `objdump` | stringhunt, dalis_kitchen |
| `gdb` / `ghidra` / static disassembly | stringhunt, dalis_kitchen |
| `debugfs` | journal_of_the_dead |
| `grep -E`, `find` | noise_hunt |
| `sox`, `audacity` | phase_phantom |
| Python 3 (`wave`, `numpy`) | phase_phantom, journal_of_the_dead, stringhunt, dalis_kitchen |

---

## Notes

- All flags follow the format `CodeandCapture{...}`.
- Solve scripts are self-contained and assume the challenge binary or file is in the same directory.
