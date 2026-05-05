# Code & Capture Challenge Writeup: Phase Phantom

**Category:** Audio Steganography · Signal Processing  
**Difficulty:** Medium  
**File:** `whistleblower_memo.wav` (44.1 kHz, 16-bit stereo, ~15 sec)

---

## Provided File

- `whistleblower_memo.wav`

---

## Technical Details

The file was constructed as follows:

- **Ambience** (A) is **in-phase** on both channels.
- **Whispered flag** (F) is **out of phase**: left channel carries `+F`, right channel carries `-F`.
- Normal playback: ambience dominates; the flag is 35–40 dB below ambient noise and spectrally similar.
- Simple mono downmix `(L+R)/2` cancels the flag completely → only ambience.
- The flag **never** appears on its own in either channel.

**The trick:** Invert one channel and sum with the other. The in-phase ambience cancels, and the out-of-phase flag increases by 6 dB.

```
L = A + F
R = A - F

L - R = (A + F) - (A - F) = 2F  ✓
```

---

## Intended Solution

### SoX (CLI)

```bash
sox whistleblower_memo.wav flag.wav remix 1,2v-1
play flag.wav gain -n -3
```

### Audacity

1. Import the stereo file.
2. Split to two mono tracks.
3. Select one track → **Effect → Invert**.
4. Select both → **Tracks → Mix → Mix and Render**.
5. Normalize and play.

### Python

```python
import wave, numpy as np

with wave.open('whistleblower_memo.wav', 'rb') as w:
    params = w.getparams()
    frames = np.frombuffer(w.readframes(params.nframes), dtype=np.int16)
    left, right = frames[0::2], frames[1::2]

recovered = (left - right).astype(np.float32)          # L - R = 2F
recovered = (recovered / np.max(np.abs(recovered)) * 32767).astype(np.int16)

with wave.open('flag.wav', 'wb') as out:
    out.setnchannels(1)
    out.setsampwidth(2)
    out.setframerate(params.framerate)
    out.writeframes(recovered.tobytes())
```

---

## Flag

```
CodeandCapture{ph4s3_inv3rs10n_r3v34ls_4ll}
```
