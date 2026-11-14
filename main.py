import sounddevice as sd
import numpy as np
from scipy.io import wavfile

# TODO:
# 1. Asf for audio file path or whether to record the audio
# 2. Ask for target SNR (needed for WGN calculation to be added to original signal)
# 3. Ask for target cutoff, suggesting ideal one (needed for filtering step to recover original signal from noise)
# 4. Save to JSON config the audio path, snr[dB], filter type (lowpass), cutoff freq

### 1. Record audio
duration = 5 # seconds
sample_rate = 44100 # Hz
audio_data = []
try:
    print(f'Recording for {duration}s...')
    recording = sd.rec(int(duration*sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
    sd.wait() # Block until recording is done
    print('Recording finished!')
    audio_data = recording.flatten() # Returns a numpy array of float32 values
except Exception as err:
    raise RuntimeError(f'Microphone error: {err}')

# Print info and write audio file
print(f'Audio data (length: {len(audio_data)}): {audio_data}')
audio_data_f = np.fft.rfft(audio_data)
print(f'Audio data freq domain (length: {len(audio_data_f)}): {audio_data_f}')
wavfile.write('test-audio.wav', sample_rate, audio_data)

### 2. Ideal cutoff freq estimation (using an energy threshold of 99.5%):
threshold = 0.995 # Energy threshold
# Take real FFT of audio signal (audio has real frequency spectrum)
audio_spectrum = np.fft.rfft(audio_data)
energy_spectrum = np.abs(audio_spectrum) ** 2 # Ignoring 1/N factor as it cancels out when we calculate the % of total energy afterwards
cumulative_energy = np.cumsum(energy_spectrum) # Each element contains the accumulated energy up to current freq bin
total_energy = cumulative_energy[-1] # Last element is the sum of all energies of each freq bin
threshold_idx = np.searchsorted(cumulative_energy, total_energy*threshold) # Find index where we hit at least 95% of the signal's energy
freqs = np.fft.rfftfreq(audio_data.size, d=1./sample_rate) # Get array of freq bins
ideal_cutoff = freqs[threshold_idx] # Corresponds to the freq where most of the signal's energy is concentrated
print(f'ideal cutoff freq: {ideal_cutoff}Hz.')


### 3. Generate White Gaussian Noise (WGN) to simulate signal transmission noise
# SNR_dB = 10log(Ps/Pn), Ps: avg signal power, Pn: avg noise power
snr_db = 15.0 # Placeholder: 5dB => noticeable noise
# To calculate a WGN satisfying the ratio, we compute the corresponding avg noise power.
# Rearranging the previous equation: 10^(SNR_dB/10) = Ps/Pn => Pn = Ps/[10^(SNR_dB/10)]
# First get avg signal power, then calculate avg noise power
avg_signal_power = np.mean(audio_data**2) # Ps
avg_noise_power = avg_signal_power/(10**(snr_db/10)) # Pn
# Now we can get the WGN, which follows a normal distribution: w[n] ~ N(0, Pn)
# By definition WGN has 0 mean and a constant deviation/variance which in this case is sqrt(Pn).
# Qualitatively this means the noise is "spread" across the whole signal
wg_noise = np.random.normal(0, np.sqrt(avg_noise_power), audio_data.shape)

# A noisy signal is just x[n] + w[n], where x[n] is out input and w[n] the WGN:
noisy_audio = audio_data + wg_noise
wavfile.write('noisy-test-audio.wav', sample_rate, noisy_audio)

#### 4. Filter to recover original signal from noisy signal
# We will use the theoretical IDEAL filter: H(f) = 1 for |f| <= fc, and 0 otherwise.
# So we just keep everything below the cutoff frequency, removing everything above it.
# This is a simplification for experimentation, not a practical filter implementation.
#
# This ideal rectangular frequency response has an abrupt discontinuity at fc. Its IFFT is
# a sinc with infinite duration, which implies an infinite impulse response in practice. Thus
# truncating in frequency produces the Gibbs phenomenon (also truncates the sinc), which produces
# "ringing" artifacts in the recovered signal (hence the abrupt discontinuity at fc).
noisy_spectrum = np.fft.rfft(noisy_audio)
freqs = np.fft.rfftfreq(noisy_audio.size, d=1./sample_rate)
noisy_spectrum[freqs > ideal_cutoff] = 0 # Apply low-pass filter
recovered_data = np.fft.irfft(noisy_spectrum, n=len(noisy_audio)) # Return to time domain
recovered_data = recovered_data.astype(np.float32) # Convert back to float32 values to be consistent with original recording
wavfile.write('recovered-test-audio.wav', sample_rate, recovered_data)
