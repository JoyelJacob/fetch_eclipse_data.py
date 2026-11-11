import urllib.request
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# Direct NOAA NCEI / LASP Solar Spectral Irradiance open CSV mirror & NASA ASTM reference
# Using direct raw CSV links so servers never return HTML query webpages
DATA_SOURCES = {
    "Reference_Solar_Spectrum_ASTM_G173": "https://githubusercontent.com",
}

def process_spectrum(name, url):
    csv_filename = f"{name}.csv"
    print(f"--- Downloading {name} ---")
    
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as response, open(csv_filename, "wb") as out_file:
        out_file.write(response.read())
        
    # Read CSV safely (skipping comment lines if any)
    df = pd.read_csv(csv_filename, comment="#")
    print("Columns found:", df.columns.tolist())
    
    # Automatically pick the first two numeric columns (Wavelength and Spectral Irradiance)
    wl_col = df.columns[0]
    int_col = df.columns[1]
    
    wavelengths = pd.to_numeric(df[wl_col], errors="coerce").to_numpy()
    intensities = pd.to_numeric(df[int_col], errors="coerce").to_numpy()
    
    # Clean invalid rows
    valid = ~np.isnan(wavelengths) & ~np.isnan(intensities)
    wavelengths = wavelengths[valid]
    intensities = intensities[valid]
    
    # Estimate background noise floor
    baseline = np.median(intensities)
    noise_std = 1.4826 * np.median(np.abs(intensities - baseline))
    threshold = baseline + (3.0 * noise_std)
    
    # Detect valid emission peaks
    peaks, _ = find_peaks(intensities, height=threshold, prominence=noise_std)
    
    if len(peaks) > 0:
        highest_wl = np.max(wavelengths[peaks])
        strongest_wl = wavelengths[peaks][np.argmax(intensities[peaks])]
        print(f"SUCCESS -> Highest (Longest) Emitted Wavelength: {highest_wl:.2f} nm")
        print(f"SUCCESS -> Strongest Peak Intensity Wavelength: {strongest_wl:.2f} nm\n")
        
        # Save plot image
        plt.figure(figsize=(10, 4))
        plt.plot(wavelengths, intensities, color="navy", linewidth=1, label="Spectral Irradiance")
        plt.scatter(wavelengths[peaks], intensities[peaks], color="orange", zorder=5, label="Detected Peaks")
        plt.axvline(highest_wl, color="green", linestyle="--", label=f"Highest WL: {highest_wl:.1f} nm")
        plt.title(f"Solar Emission Spectrum Analysis ({name})")
        plt.xlabel("Wavelength (nm)")
        plt.ylabel("Spectral Irradiance (W/m^2/nm)")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig(f"{name}_plot.png", dpi=150)
        plt.close()
        print(f"Saved chart to {name}_plot.png")
    else:
        print("No peaks detected above threshold.")

if __name__ == "__main__":
    for name, url in DATA_SOURCES.items():
        process_spectrum(name, url)
