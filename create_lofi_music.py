import wave
import math
import struct
import random

def generate_lofi_track(filename="lofi_track.wav", duration=40.0, sample_rate=44100):
    bpm = 84
    beat_dur = 60.0 / bpm
    total_samples = int(duration * sample_rate)
    
    # Frequencies for chords (Cmaj7 -> Am7 -> Fmaj7 -> G7)
    chords = [
        [261.63, 329.63, 392.00, 493.88], # Cmaj7
        [220.00, 261.63, 329.63, 392.00], # Am7
        [174.61, 220.00, 261.63, 329.63], # Fmaj7
        [196.00, 246.94, 293.66, 349.23]  # G7
    ]
    
    audio = [0.0] * total_samples
    
    num_beats = int(duration / beat_dur)
    
    for b in range(num_beats):
        beat_start_time = b * beat_dur
        beat_start_idx = int(beat_start_time * sample_rate)
        chord = chords[(b // 4) % len(chords)]
        
        # 1. Piano / Rhodes Chord synth on beat 0 and 2.5 of a bar
        if b % 4 == 0 or b % 4 == 2:
            chord_dur = beat_dur * 1.8
            chord_samples = int(chord_dur * sample_rate)
            for i in range(min(chord_samples, total_samples - beat_start_idx)):
                t = i / sample_rate
                env = math.exp(-t * 2.5) # Soft decay
                sample_val = 0.0
                for freq in chord:
                    # Warm sine + fundamental
                    sample_val += math.sin(2 * math.pi * freq * t) * 0.15
                    sample_val += math.sin(2 * math.pi * freq * 2 * t) * 0.03 # subtle harmonic
                audio[beat_start_idx + i] += sample_val * env
                
        # 2. Bassline
        bass_freq = chord[0] / 2.0
        bass_dur = beat_dur * 0.9
        bass_samples = int(bass_dur * sample_rate)
        for i in range(min(bass_samples, total_samples - beat_start_idx)):
            t = i / sample_rate
            env = math.exp(-t * 3.0)
            sample_val = math.sin(2 * math.pi * bass_freq * t) * 0.25
            audio[beat_start_idx + i] += sample_val * env

        # 3. Lo-Fi Drums (Kick on 0 & 3, Snare on 2, Hi-hat on 0,1,2,3)
        # Kick (beat 0 & 2.5)
        if b % 4 == 0 or (b % 4 == 2 and random.random() > 0.4):
            kick_dur = 0.12
            kick_samples = int(kick_dur * sample_rate)
            for i in range(min(kick_samples, total_samples - beat_start_idx)):
                t = i / sample_rate
                freq = 130 * math.exp(-t * 35) # Frequency sweep
                env = math.exp(-t * 15)
                audio[beat_start_idx + i] += math.sin(2 * math.pi * freq * t) * 0.4 * env
                
        # Snare (beat 2)
        if b % 4 == 2:
            snare_dur = 0.15
            snare_samples = int(snare_dur * sample_rate)
            for i in range(min(snare_samples, total_samples - beat_start_idx)):
                t = i / sample_rate
                env = math.exp(-t * 20)
                noise = (random.random() * 2 - 1) * 0.2
                tone = math.sin(2 * math.pi * 180 * t) * 0.15
                audio[beat_start_idx + i] += (noise + tone) * env
                
        # Hi-Hat (every beat)
        hat_dur = 0.05
        hat_samples = int(hat_dur * sample_rate)
        for i in range(min(hat_samples, total_samples - beat_start_idx)):
            t = i / sample_rate
            env = math.exp(-t * 60)
            noise = (random.random() * 2 - 1) * 0.08
            audio[beat_start_idx + i] += noise * env
            
    # Add subtle vinyl crackle warmth
    for i in range(total_samples):
        if random.random() < 0.002:
            audio[i] += (random.random() - 0.5) * 0.05

    # Normalize audio to prevent clipping
    max_val = max(abs(x) for x in audio) or 1.0
    scaling = 28000.0 / max_val
    
    with wave.open(filename, "w") as wf:
        wf.setnchannels(1) # Mono
        wf.setsampwidth(2) # 16-bit
        wf.setframerate(sample_rate)
        packed_data = bytearray()
        for x in audio:
            sample_int = int(x * scaling)
            sample_int = max(-32768, min(32767, sample_int))
            packed_data.extend(struct.pack("<h", sample_int))
        wf.writeframes(packed_data)
        
    print(f"Lo-fi background music generated: {filename}")

if __name__ == "__main__":
    generate_lofi_track()
