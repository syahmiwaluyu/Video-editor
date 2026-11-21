import json, sys
from faster_whisper import WhisperModel
m = WhisperModel("large-v3", device="cpu", compute_type="int8", cpu_threads=4)
import wave, numpy as np
w=wave.open("audio16k.wav"); a=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768
segs, info = m.transcribe(a, language="en", word_timestamps=True, vad_filter=True, beam_size=5,
    initial_prompt="A Malaysian healthcare worker talks with a counsellor after a difficult resuscitation case. Hospital, nurse, doctor, patient, ward, CPR.")
out=[]
for s in segs:
    out.append({"start":s.start,"end":s.end,"text":s.text.strip(),"words":[{"w":w.word,"s":w.start,"e":w.end,"p":w.probability} for w in s.words]})
    print(f"[{s.start:7.2f}-{s.end:7.2f}] {s.text.strip()}", flush=True)
json.dump(out, open("transcript.json","w"), ensure_ascii=False, indent=1)
print("DONE", flush=True)
