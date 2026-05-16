import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile

def main():
    # 1. Cargar datos
    fs, audio = wavfile.read('prueba.wav')
    if audio.dtype == np.int16:
        audio = audio.astype(np.float32) / 32768.0

    try:
        f0 = np.loadtxt('prueba.f0')
    except:
        return

    try:
        features = np.loadtxt('features.dat')
        pot = features[:, 0]
        r1norm = features[:, 1]
        rmaxnorm = features[:, 2]
    except:
        return

    try:
        f0ref = np.loadtxt('prueba.f0ref')
    except:
        return

    # Alinear
    min_len = min(len(f0), len(pot))
    if len(f0) > len(pot):
        f0_feat = f0[1:min_len+1]
    else:
        f0_feat = f0[:min_len]

    pot = pot[:min_len]
    r1norm = r1norm[:min_len]
    rmaxnorm = rmaxnorm[:min_len]

    time_axis_feat = np.arange(min_len) * 0.015
    time_axis_audio = np.arange(len(audio)) / fs

    # --- GRAFICA 1: CARACTERISTICAS ---
    fig, axs = plt.subplots(4, 1, figsize=(10, 10), sharex=True)
    
    axs[0].plot(time_axis_audio, audio, color='gray', alpha=0.7)
    axs[0].set_title('Señal de audio')
    axs[0].set_ylabel('Amplitud')

    axs[1].plot(time_axis_feat, pot, 'k-')
    axs[1].axhline(y=-50, color='r', linestyle='--')
    axs[1].set_title('Nivel de potencia (pot)')
    axs[1].set_ylabel('dB')

    axs[2].plot(time_axis_feat, r1norm, 'b-')
    axs[2].axhline(y=0.4, color='r', linestyle='--')
    axs[2].set_title('Autocorrelación normalizada de 1 (r1norm)')
    axs[2].set_ylabel('Valor')

    axs[3].plot(time_axis_feat, rmaxnorm, 'm-')
    axs[3].axhline(y=0.4, color='r', linestyle='--')
    axs[3].set_title('Autocorrelación en el máximo secundario (rmaxnorm)')
    axs[3].set_xlabel('Tiempo (s)')
    axs[3].set_ylabel('Valor')

    plt.tight_layout()
    plt.savefig('features_plot.png')
    plt.close()

    # --- GRAFICA 2: COMPARACION ---
    # f0 and f0ref might have slightly different lengths. We plot them together
    time_axis_f0 = np.arange(len(f0)) * 0.015
    time_axis_f0ref = np.arange(len(f0ref)) * 0.015

    plt.figure(figsize=(10, 4))
    
    # avoid plotting the 0 values to make it look like wavesurfer pitch contours
    f0_plot = np.where(f0 == 0, np.nan, f0)
    f0ref_plot = np.where(f0ref == 0, np.nan, f0ref)

    plt.plot(time_axis_f0ref, f0ref_plot, 'b.-', label='Referencia (Wavesurfer)', linewidth=2, markersize=8)
    plt.plot(time_axis_f0, f0_plot, 'r.-', label='Nuestro estimador (.f0)', linewidth=1.5, markersize=5)
    
    plt.title('Comparación de estimadores de Pitch')
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Frecuencia (Hz)')
    plt.legend()
    plt.grid(True, linestyle=':', alpha=0.6)
    
    plt.tight_layout()
    plt.savefig('compare_plot.png')
    plt.close()

if __name__ == '__main__':
    main()
