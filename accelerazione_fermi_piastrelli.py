import sys
import numpy as np
import pandas as pd
import scipy
import math
import random
import emcee
import corner
import time
from scipy.optimize import curve_fit

import matplotlib.pyplot as plt
from scipy.stats import linregress

# Funzione di partenza
def power_law(E, a, gamma):
    return a*E**(-gamma)

# Classe per il Random Walk
class FermiRandomWalk:
	def __init__(self, step_init, n_steps, x_init, gain, config, xmax_init=None):
		#Inizializzazione parametri del moto
		self.step = step_init
		self.n_steps = n_steps
		self.x = x_init
		self.gain = gain
		self.config = config
		self.xmax = xmax_init
		self.xmax_decay = 0.99 if xmax_init else None
		self.positions = [x_init]
		self.steps = [step_init]
	def walk(self):
		x = self.x
		step = self.step
		xmax = self.xmax
		
		for _ in range(self.n_steps):
			direction = np.random.choice([-1, 1])
			x_new = x + direction * step
			
			if self.config == "attraversamento_origine":
				if ( x>0 and x_new<=0) or (x<0 and x_new>=0):
					step *= self.gain    #come se fosse step = step*self.gain
			elif self.config == "doppia_riflessione":
				if x>0 and x_new<=0:
					x_new = -x_new
					step *= self.gain
				elif xmax and abs(x_new) >= xmax:
					x_new = 2 * xmax - abs(xnew)
					xmax *= self.xmax_decay
			elif self.config == "doppia_accelerazione":
				if x>0 and x_new<=0:
					x_new = -x_new
					step *= self.gain
				elif xmax and abs(x_new) >= xmax:
					x_new = 2 * xmax - abs(x_new)
					step *= self.gain
					xmax *= self.xmax_decay
			
			x = x_new
			self.positions.append(x)
			self.steps.append(step)
		
		return self.positions, self.steps

# Funzione per analizzare la distribuzione dell'energia e stimare gamma (senza usare log)
def analyze_energy_distribution_nolog(steps, config_name):
    energy = np.array(steps)     # Trasforma la lista in array numpy
    energy = energy[energy>0]    # Elimina eventuali valori negativi o zero
	
    # Calcolo istogramma con gestione dinamica dei bin
    for bins_ in [50, 30, 20, 10]:# Prova a ridurre i bin se troppo pochi punti
        hist, bin_edges = np.histogram(energy, bins=bins_, density=True)
        bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
        mask = hist > 0
        x = bin_centers[mask]
        y = hist[mask]
        
        if len(x) >= 2:
            break  # Esci se ci sono abbastanza punti per il fit
        
    if len(x) < 2:
        print(f"Fit non eseguibile per {config_name}: solo {len(x)} punto/i disponibili anche dopo riduzione bin")
        return None


	# Forza gli array a essere 1D
    x = np.asarray(x).flatten()
    y = np.asarray(y).flatten()
    
	# Tentativo di Fit della funzione esponenziale per stimare a e gamma
    try:
        popt, _ = curve_fit(power_law, x, y, p0=(1, 1), maxfev=10000)  # Stima iniziale
        a_fit, gamma_fit = popt
    except RuntimeError:
        print(f"Errore nel fit per {config_name}: parametri ottimali non trovati")
        return None

	# Grafico dell'istogramma + Curva di fit
    plt.figure(figsize=(6,5))
    plt.hist(energy, bins=50, density=True, color='skyblue', edgecolor='black', label='Dati')
    x_fit = np.linspace(min(x), max(x), 200)
    plt.plot(x_fit, power_law(x_fit, *popt), 'r--', label=f'Fit: gamma = {gamma_fit:.2f}')
    plt.title(f"Distribuzione energia - {config_name}")
    plt.xlabel("Energia (lunghezza del passo)")
    plt.ylabel("Frequenza relativa")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    return gamma_fit


# Funzione che esegue una simulazione completa per una data configurazione
def test_config(step_init, n_steps, x_init, gain, xmax_init=100.0):
    configs = ["attraversamento_origine", "doppia_riflessione", "doppia_accelerazione"]

    for config_name in configs:
        print(f"\n--- Simulazione: {config_name} ---\n")
        # Crea un oggetto FermiRandomWalk con i parametri iniziali
        # (Test effettuati con 1.0, 1000, 10.0, 1.01, "100.0")
        walk = FermiRandomWalk(
            step_init=step_init,             # Lunghezza iniziale del passo
            n_steps=n_steps,             # Nummero totale di passi
            x_init=x_init,             # Posizione iniziale
            gain=gain,              # Fattore di accelerazione
            config=config_name,           # Tipo di configurazione (origine, riflessione, accelerazione)
            xmax_init=xmax_init              # Valore massimo "a destra" (se usato)
        )
        # Simula il cammino
        positions, steps = walk.walk()

        # Grafico della posizione e della lunghezza dei passi nel tempo
        plt.figure(figsize=(12, 10))
        plt.subplot(2, 1, 1)
        plt.plot(positions)
        plt.title(f"Posizione - {config_name}")
        plt.xlabel("Passi")
        plt.ylabel("Posizione")

        plt.subplot(2, 1, 2)
        plt.plot(steps)
        plt.title(f"Lunghezza del passo - {config_name}")
        plt.xlabel("Passi")
        plt.ylabel("Lunghezza passo")

        plt.subplots_adjust(hspace=0.5)
        plt.show()
        
        # Analizza la distribuzione dell'energia e stampa gamma
        gamma = analyze_energy_distribution_nolog(steps, config_name)
        if gamma:
            print(f"Stima dell'indice spettrale γ per {config_name}: {gamma:.2f}")

# Inizializzazione simulazione con scelta dei parametri
if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Uso: python3 bozza_progetto_2.py <step_init> <n_steps> <x_init> <gain>")
        sys.exit(1)

    step_init = float(sys.argv[1])
    n_steps = int(sys.argv[2])
    x_init = float(sys.argv[3])
    gain = float(sys.argv[4])

    test_config(step_init, n_steps, x_init, gain)




