import numpy as np
import matplotlib.pyplot as plt

def main():
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

    min_len = min(len(f0), len(pot))
    if len(f0) > len(pot):
        f0_feat = f0[1:min_len+1]
    else:
        f0_feat = f0[:min_len]

    pot = pot[:min_len]
    r1norm = r1norm[:min_len]
    rmaxnorm = rmaxnorm[:min_len]

    frame_axis_feat = np.arange(min_len)
    frame_axis_f0ref = np.arange(len(f0ref))

    fig, axs = plt.subplots(4, 1, figsize=(10, 10), sharex=True)
    
    axs[0].plot(frame_axis_f0ref, f0ref, 'b-', label='Estimación Wavesurfer', linewidth=2)
    axs[0].set_title('Estimación de pitch (Wavesurfer)')
    axs[0].set_ylabel('Frecuencia (Hz)')
    axs[0].set_ylim(0, 500)

    axs[1].plot(frame_axis_feat, pot, 'k-')
    axs[1].axhline(y=-50, color='r', linestyle='--')
    axs[1].set_title('Nivel de potencia (pot)')
    axs[1].set_ylabel('dB')

    axs[2].plot(frame_axis_feat, r1norm, 'b-')
    axs[2].axhline(y=0.4, color='r', linestyle='--')
    axs[2].set_title('Autocorrelación normalizada de 1 (r1norm)')
    axs[2].set_ylabel('Valor')

    axs[3].plot(frame_axis_feat, rmaxnorm, 'm-')
    axs[3].axhline(y=0.4, color='r', linestyle='--')
    axs[3].set_title('Autocorrelación en el máximo secundario (rmaxnorm)')
    axs[3].set_xlabel('Trama')
    axs[3].set_ylabel('Valor')

    plt.tight_layout()
    plt.savefig('features_plot.png')
    plt.close()

    frame_axis_f0 = np.arange(len(f0))

    plt.figure(figsize=(10, 4))
    
    plt.plot(frame_axis_f0ref, f0ref, 'b-', label='Referencia (Wavesurfer)', linewidth=2)
    plt.plot(frame_axis_f0, f0, 'r-', label='Nuestro estimador (.f0)', linewidth=1.5)
    
    plt.title('Comparación de estimadores de Pitch')
    plt.xlabel('Trama')
    plt.ylabel('Frecuencia (Hz)')
    plt.ylim(0, 500)
    plt.legend()
    plt.grid(True, linestyle=':', alpha=0.6)
    
    plt.tight_layout()
    plt.savefig('compare_plot.png')
    plt.close()

if __name__ == '__main__':
    main()
