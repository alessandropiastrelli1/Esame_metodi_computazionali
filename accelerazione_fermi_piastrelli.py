import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import sys

# Funzione di potenza per il fit: N(E) = a * E^(-gamma)
def power_law(E, a, gamma):
    return a * E ** (-gamma)

# Classe per Random Walk con accelerazione di Fermi (con più walker)
class FermiRandomWalk:
    # Inizializza i parametri del camminatore
    def __init__(self, n_walkers, step_init, n_steps, x_init, gain, config, xmax_init=None, seed=None):
        self.n_walkers = n_walkers
        self.step_init = step_init
        self.n_steps = n_steps
        self.x_init = x_init
        self.gain = gain
        self.config = config
        self.xmax = xmax_init
        self.xmax_decay = 0.99 if xmax_init else None
        #self.rng = np.random.default_rng(seed)
        if seed is not None:
            np.random.seed(seed)

    # Esegue il random walk per tutti i walker
    def walk(self):
        x = np.full(self.n_walkers, self.x_init)
        step = np.full(self.n_walkers, self.step_init)
        xmax_array = np.full(self.n_walkers, self.xmax)   # E' un array "dinamico" per ogni walker

        positions = [x.copy()]
        steps = [step.copy()]

        for step_i in range(self.n_steps):
            direction = 2 * np.random.randint(0, 2, size=self.n_walkers) - 1
            x_new = x + direction * step

            if self.config == "attraversamento_origine":
                crossed = ((x > 0) & (x_new <= 0)) | ((x < 0) & (x_new >= 0))
                step[crossed] *= self.gain

            elif self.config == "doppia_riflessione":
                reflect_left = (x > 0) & (x_new <= 0)
                x_new[reflect_left] = -x_new[reflect_left]
                step[reflect_left] *= self.gain

                reflect_right = np.abs(x_new) >= xmax_array
                x_new[reflect_right] = 2 * xmax_array[reflect_right] - np.abs(x_new[reflect_right])
                xmax_array[reflect_right] *= self.xmax_decay

            elif self.config == "doppia_accelerazione":
                reflect_left = (x > 0) & (x_new <= 0)
                x_new[reflect_left] = -x_new[reflect_left]
                step[reflect_left] *= self.gain

                reflect_right = np.abs(x_new) >= xmax_array
                x_new[reflect_right] = 2 * xmax_array[reflect_right] - np.abs(x_new[reflect_right])
                step[reflect_right] *= self.gain
                xmax_array[reflect_right] *= self.xmax_decay

            x = x_new
            positions.append(x.copy())
            steps.append(step.copy())

        return np.array(positions), np.array(steps)

# Analizza la distribuzione delle energie finali e calcola gamma (senza scala log)
def analyze_energy_distribution(steps, config_name):
    energy = steps[-1][steps[-1] > 0]  # Ultimo passo di tutti i walker

    for bins in [50, 30, 20, 10]:  # Prova diversi bin finché ci sono abbastanza dati
        hist, bin_edges = np.histogram(energy, bins=bins, density=True)
        bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
        mask = hist > 0
        x = bin_centers[mask]
        y = hist[mask]
        if len(x) >= 2:
            break

    if len(x) < 2:
        print(f"Fit non eseguibile per {config_name}: solo {len(x)} punto/i disponibili")
        return None

	# Forza gli array a essere 1D (Utilizzato per testare il funzionamento nel caso "doppia_accelerazione")
    #x = np.asarray(x).flatten()
    #y = np.asarray(y).flatten()    
    
    try:
        if len(x) < 3 or np.max(y) < 1e-5:
            print(f"Dati insufficienti o troppo piatti per {config_name}")
            return None
        popt, _ = curve_fit(
            power_law,
            x, y,
            p0=(np.max(y), 1.5),
            #bounds=([1e-8, 0.1], [1e3, 5]),
            maxfev=10000
        )
        a_fit, gamma_fit = popt
    except RuntimeError:
        print(f"Fit fallito per {config_name}")
        return None

    # Grafico della distribuzione e del fit
    plt.figure(figsize=(6, 5))
    plt.hist(energy, bins=50, density=True, color='skyblue', edgecolor='black', label='Dati')
    x_fit = np.linspace(min(x), max(x), 200)
    plt.plot(x_fit, power_law(x_fit, *popt), 'r--', label=f'Fit: γ = {gamma_fit:.3f}')
    plt.title(f"Distribuzione energia - {config_name}")
    plt.xlabel("Energia (lunghezza del passo)")
    plt.ylabel("Frequenza relativa")
    plt.legend()
    plt.grid(True)
    #plt.tight_layout()
    plt.show()

    return gamma_fit

# Esegue la simulazione per tutte le configurazioni richieste
def run_all_configs(n_walkers, step_init, n_steps, x_init, gain, xmax_init=80.0):
    configs = ["attraversamento_origine", "doppia_riflessione", "doppia_accelerazione"]
    for config_name in configs:
        print(f"\n--- Simulazione: {config_name} ---\n")
        walk = FermiRandomWalk(n_walkers, step_init, n_steps, x_init, gain, config_name, xmax_init)
        positions, steps = walk.walk()

        # Plot di posizione e passo per alcuni camminatori
        plt.figure(figsize=(12, 20))
        plt.subplot(2, 1, 1)
        for i in range(min(10, n_walkers)):
            plt.plot(positions[:, i], alpha=0.6)
        plt.title(f"Posizione - {config_name}")
        plt.xlabel("Passi")
        plt.ylabel("Posizione")

        plt.subplot(2, 1, 2)
        for i in range(min(10, n_walkers)):
            plt.plot(steps[:, i], alpha=0.6)
        plt.title(f"Lunghezza del passo - {config_name}")
        plt.xlabel("Passi")
        plt.ylabel("Lunghezza passo")

        plt.subplots_adjust(hspace=0.5)
        plt.show()

        gamma = analyze_energy_distribution(steps, config_name)
        if gamma:
            print(f"Stima dell'indice spettrale γ per {config_name}: {gamma:.2f}")

# Acquisisce i parametri dal prompt e avvia la simulazione
if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Uso: python3 script.py <n_walkers> <step_init> <n_steps> <x_init> <gain>")
        sys.exit(1)

    n_walkers = int(sys.argv[1])
    step_init = float(sys.argv[2])
    n_steps = int(sys.argv[3])
    x_init = float(sys.argv[4])
    gain = float(sys.argv[5])

    run_all_configs(n_walkers, step_init, n_steps, x_init, gain)

