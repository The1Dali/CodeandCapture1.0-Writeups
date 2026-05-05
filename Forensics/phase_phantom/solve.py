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