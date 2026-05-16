import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
import sys

def autocorr(x):
    result = np.correlate(x, x, mode='full')
    return result[result.size // 2:] / len(x)

def find_pitch_peak(r, fs, min_f0=50, max_f0=500):
    npitch_min = int(fs / max_f0)
    npitch_max = int(fs / min_f0)
    
    # Find first negative value
    first_negative = 1
    while first_negative < len(r) and r[first_negative] >= 0:
        first_negative += 1
        
    search_start = max(first_negative, npitch_min)
    if search_start >= len(r) or search_start >= npitch_max:
        return 0, 0
        
    search_end = min(npitch_max, len(r))
    
    lag_max = search_start + np.argmax(r[search_start:search_end])
    return lag_max, r[lag_max]

def main():
    wav_path = 'prueba.wav'
    fs, data = wavfile.read(wav_path)
    
    # Normalize data
    if data.dtype == np.int16:
        data = data.astype(np.float32) / 32768.0
    
    # We need a 30 ms voiced segment
    # Let's take a segment around the middle of the file where speech is likely
    frame_len = int(0.030 * fs)
    # manually select a start index that is voiced. Let's try 1.5 seconds in
    start_idx = int(1.5 * fs)
    
    # Find a highly energetic frame near start_idx to ensure it's voiced
    max_energy = 0
    best_start = start_idx
    for i in range(start_idx, start_idx + 2*fs, frame_len):
        frame = data[i:i+frame_len]
        energy = np.sum(frame**2)
        if energy > max_energy:
            max_energy = energy
            best_start = i
            
    x = data[best_start:best_start+frame_len]
    
    # apply hamming window
    window = np.hamming(frame_len)
    x_win = x * window
    
    r = autocorr(x_win)
    
    lag_max, r_max = find_pitch_peak(r, fs)
    pitch_period_s = lag_max / fs
    f0 = fs / lag_max if lag_max > 0 else 0
    
    # Plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    time_axis = np.arange(frame_len) / fs
    ax1.plot(time_axis * 1000, x)
    ax1.set_title(f'Segmento temporal (30 ms) - Voiced (F0 estimado: {f0:.1f} Hz)')
    ax1.set_xlabel('Tiempo (ms)')
    ax1.set_ylabel('Amplitud')
    # Mark pitch period
    if lag_max > 0:
        ax1.axvline(x=0, color='r', linestyle='--', alpha=0.5)
        ax1.axvline(x=pitch_period_s * 1000, color='r', linestyle='--', alpha=0.5, label='Periodo de Pitch (T0)')
        ax1.legend()
    
    lag_axis = np.arange(len(r)) / fs
    ax2.plot(lag_axis * 1000, r)
    ax2.set_title('Autocorrelación')
    ax2.set_xlabel('Lag (ms)')
    ax2.set_ylabel('r[l]')
    if lag_max > 0:
        ax2.plot(lag_max / fs * 1000, r_max, 'ro', label=f'Primer máximo secundario ({lag_max/fs*1000:.1f} ms)')
        ax2.legend()
        
    plt.tight_layout()
    plt.savefig('autocorr_plot.png')
    print(f"Saved plot to autocorr_plot.png. F0: {f0:.1f} Hz")

if __name__ == '__main__':
    main()
