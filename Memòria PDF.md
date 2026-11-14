# Proposta de Projecte: Simulador de Transmissió i Filtratge de Senyals d’Àudio amb Soroll

*Adaptació de la Proposta 7: Simulador de transmissió de senyals amb soroll*

## 1. Equip

* **Membres:** [Ricardo Christmann] (NIU: 1798330) i [Martí Carreras Serra] (NIU: 1792315).
* **Repartiment de responsabilitats:**
* *DSP i algoritmes:* Disseny de les classes del senyal, canal i filtre (`dsp.py`), càlcul espectral (FFT: Fast Fourier Transform) i mètriques d'error (`metrics.py`).
* *Interfície terminal, persistència i proves:* Flux interactiu de terminal (`main.py`), gestió de configuracions (`config_manager.py`), validació d'errors i tests unitaris.

## 2. Context

En qualsevol sistema de comunicacions, la transmissió d’un senyal a través d’un medi físic introdueix sorolls, modelades habitualment com a **Ruido Blanco Gaussiano Aditivo (AWGN: Additive White Gaussian Noise)** en funció de la **Relació Senyal-Soroll (SNR: Signal-to-Noise Ratio)**. En lloc de generar dades simulades/"fake" o dependre de maquinari de radiofreqüència (SDR), aplicar aquests models sobre **senyals d’àudio digital** (fitxers `.wav` o captura per micròfon) permet treballar amb dades reals i avaluar el resultat tant matemàticament com escoltant directament l'àudio amb soroll o l'àudio recuperat.

## 3. Problema

El soroll blanc reparteix la seva potència de manera uniforme per tot l’espectre disponible, fins a la freqüència màxima que permet el mostreig del fitxer (**Teorema de Nyquist**, $B < f_s / 2$). En canvi, la informació útil d’un senyal acústic (com la veu humana) es concentra en una banda de freqüències molt més estreta. Sense filtratge, el soroll d'alta freqüència degrada severament el senyal; però si un usuari configura una freqüència de tall arbitrària, pot eliminar contingut rellevant del missatge o provocar errors matemàtics en superar el límit de Nyquist. A més, cal acotar de manera realista què pot eliminar un filtre lineal (soroll fora de banda) i què roman inevitablement (soroll dins de banda).

## 4. Utilitat

* **Validació pràctica i audible:** Permet experimentar com afecta una determinada SNR (en dB) a un senyal real i comprovar la millora obtinguda després de filtrar-lo, tant a nivell numèric (MSE: Mean Squared Error) com perceptiu (escoltar els audios obtinguts).
* **Assistència automàtica a l'usuari:** Mitjançant l'anàlisi de l'espectre amb la FFT, el programa estima l'amplada de banda on es concentra la major part de l'energia del senyal (p. ex. 99,5%) i proposa una freqüència de tall recomanada per defecte.
* **Reproductibilitat:** Desar els paràmetres d'entrada en format `JSON` i exportar les mètriques de cada execució en `CSV` facilita comparar diferents configuracions i audios sense modificar el codi.

## 5. Objectiu

Desenvolupar una aplicació de terminal modular en Python que simuli la transmissió d’un senyal d’àudio d'un canal (mono) amb soroll AWGN i la seva posterior recuperació mitjançant un filtre passabaix ideal en freqüència, complint els criteris:

1. Estructurar el codi en mòduls i classes POO (`AudioSignal`, `Channel`, `Filter`).
2. Implementar algoritmes d'anàlisi espectral (estimació d'energia amb FFT), simulació de canal sorollós i filtratge en el domini freqüencial.
3. Tractar de manera robusta les entrades invàlides (comprovació del límit de Nyquist, rebuig d'àudio multi-canal, fitxers inexistents o valors no numèrics) i verificar el funcionament mitjançant proves unitàries.
4. Persistència de dades mitjançant fitxers `.wav` (audio), `JSON` (configuració) i `CSV` (mètriques d'error).

En efecte, és un projecte alineat amb els conceptes estudiats a les assignatures de "Fonaments d'Enginyeria del Software" i "Senyals i Sistemes Discrets".

## 6. Abast del projecte

### Primer abast de l’MVP
* **Arquitectura bàsica:** Separació inicial en mòduls (`main.py`, `dsp.py`, `config_manager.py`) amb les classes principals (`AudioSignal`, `Channel`, `Filter`) fent servir llibreries estàndard de càlcul científic ([`numpy`](https://numpy.org/doc/stable/index.html) i [`scipy.io.wavfile`](https://docs.scipy.org/doc/scipy/reference/io.html#module-scipy.io.wavfile)).
* **Processament principal:** Lectura d'un fitxer `.wav` (mono) mitjançant paràmetres definits a `simulation_config.json`, injecció de soroll blanc (WGN) segons la SNR, filtratge passabaix ideal amb `rfft`/`irfft` (amb freqüència de tall manual o estimada per energia) i càlcul del MSE abans i després del filtratge.
* **Sortida bàsica:** Exportació dels fitxers `noisy_audio.wav` i `recovered_audio.wav` i visualització de les mètriques per terminal.

### Ampliacions per a la versió final (Post-MVP)
* **Captura per micròfon:** Integració de [`sounddevice`](https://python-sounddevice.readthedocs.io/en/0.5.3/) per gravar àudio en directe com a alternativa a la càrrega de fitxers `.wav`.
* **Assistent interactiu i validació completa:** Menú de terminal amb bucles de control d'errors (comprovació del límit de Nyquist, detecció d'àudio multi-canal, gestió d'errors).
* **Registre històric i proves:** Exportació automàtica dels resultats de cada execució a `simulation_history.csv` (`metrics.py`) i tests unitaris.

### Fora de l'abast (Limitacions assumides)
* **Àudio multi-canal (estèreo):** El sistema treballa exclusivament amb senyals d'un sol canal (mono). Els fitxers estèreo es detecten i es rebutgen amb un missatge d'error en lloc de mesclar-los.
* **Filtres digitals avançats o reducció de soroll no lineal:** No s'implementen filtres IIR/FIR d'ordre superior (com Butterworth o Chebyshev, accessibles a través de `scipy`) ni tècniques "avançades" per eliminar soroll residual, i.e. el filtratge es limita a un tall ideal en freqüència. Només apliquem el que hem après fins ara a la carrera.
* **Interfície gràfica (GUI):** Tota la interacció es realitza pel terminal amb menús senzills.
