# Code & Capture Challenge Writeup: NoiseHunt

**Category:** Forensics / Linux CLI  
**Difficulty:** Beginner-Intermediate  

---

## Challenge Description

You are given a directory called `haystack` containing multiple subfolders and over 40 text files filled with lorem ipsum text and dozens of fake flag-like strings.

The goal is to find the **real flag**, which is the only one that matches this exact pattern:

```
CodeandCapture{[a-z0-9_]{40,}}
```

All other `CodeandCapture{` strings are noise designed to trick simple searches.

---

## Solution Walkthrough

### Step 1: Explore the directory structure

```bash
cd ctf_challenge
ls -R
```

This shows subfolders like `archive/`, `documents/`, `logs/`, `configs/`, etc., each containing several `.txt` files.

### Step 2: Quick (but noisy) search for any flag

A basic recursive search shows many false positives:

```bash
grep -r "CodeandCapture{" .
```

You will see lots of fake flags such as:

```
CodeandCapture{short}
C0deandCapture{nope}
CodeAndCapture{wrongcase}
CodeandCapture{invalid@symbol}
```

This demonstrates why a simple string search is not enough.

### Step 3: Use Extended Regular Expressions (`-E`) to filter the real flag

The real flag is longer (more than 40 characters inside the braces) and contains only lowercase letters, digits, and underscores.

Run this command:

```bash
grep -r -E 'CodeandCapture\{[a-z0-9_]{40,}\}' .
```

Breakdown of the regex:

- `CodeandCapture\{` → literal `CodeandCapture{` (the backslash escapes the `{`)
- `[a-z0-9_]` → any lowercase letter, digit, or underscore
- `{40,}` → repeated 40 or more times
- `\}` → literal closing brace

Expected output:

```
documents/confidential_notes.txt:The secure token is: CodeandCapture{you_mastered_grep_and_regex_in_this_ctf_challenge_d4t4_h1d1ng_7f3a2b}
```

### Alternative commands (more advanced techniques)

Using `find + grep` (shows only the filename first):

```bash
find . -type f -exec grep -l -E 'CodeandCapture\{[a-z0-9_]{40,}\}' {} +
```

Case-insensitive version (if you want to experiment):

```bash
grep -r -E -i 'codeandcapture\{[a-z0-9_]{40,}\}' .
```

Using `rg` (ripgrep) if installed (much faster on large directories):

```bash
rg -e 'CodeandCapture\{[a-z0-9_]{40,}\}'
```

### Step 4: Verify the flag

Open the file to see the context:

```bash
cat documents/confidential_notes.txt | grep -E 'CodeandCapture\{[a-z0-9_]{40,}\}'
```

Or simply:

```bash
cat documents/confidential_notes.txt
```

You will see the flag embedded in a fake "internal memo" surrounded by lorem ipsum and more fake flags.

---

## Flag

```
CodeandCapture{you_mastered_grep_and_regex_in_this_ctf_challenge_d4t4_h1d1ng_7f3a2b}
```

---

## Lessons Learned

Always use regular expressions when dealing with noisy data. `grep -r -E` (or `egrep`) is extremely powerful for pattern matching across many files. `find -exec` is useful when you need to combine file searching with content searching. In real CTFs, flags are often hidden among thousands of lines or files — regex saves the day.

---

## Bonus Challenges (for extra practice)

- Solve it without using the `-E` flag (only basic grep + other tools).
- Find the file using only `find` and `strings`.
- Write a one-liner that outputs only the flag (no extra text).
