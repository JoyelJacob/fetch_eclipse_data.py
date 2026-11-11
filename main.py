import urllib.request
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# 1. Exact dates of the last 3 solar eclipses
eclipse_dates = {
    "2025-09-21_partial": "2025-09-21",
    "2026-02-17_annular": "2026-02-17",
    "2026-08-12_total":   "2026-08-12"
}

# NASA / LASP TSIS-1 Solar Spectral Irradiance API (200 nm to 2400 nm)
base_url = "https://colorado.edu"

for label, date_str in eclipse_dates.items():
    query_url = f"{base_url}?time>={date_str}T00:00:00Z&time<={date_str}T23:59:59Z"
    csv_filename = f"{label}_spectrum.csv"
    
    print(f"--- Processing {label} ({date_str}) ---")
    try:
        # Step A: Download the real dataset for this eclipse day
        urllib.request.urlretrieve(query_url, csv_filename)
        df = pd.read_csv(csv_filename)
        
        # Identify wavelength and irradiance columns automatically
        wl_col = [c for c in df.columns if "wavelength" in c.lower()][0]
        int_col = [c for c in df.columns if "irradiance" in c.lower()][0]
        
        wavelengths = pd.to_numeric(df[wl_col], errors="coerce").to_numpy()
        intensities = pd.to_numeric(df[int_col], errors="coerce").to_numpy()
        
        # Remove empty/NaN values
        valid = ~np.isnan(wavelengths) & ~np.isnan(intensities)
        wavelengths = wavelengths[valid]
        intensities = intensities[valid]
        
        # Step B: Estimate background noise floor
        baseline = np.median(intensities)
        noise_std = 1.4826 * np.median(np.abs(intensities - baseline))
        threshold = baseline + (3.0 * noise_std)
        
        # Step C: Find emission peaks above noise
        peaks, _ = find_peaks(intensities, height=threshold, prominence=noise_std)
        
        if len(peaks) > 0:
            highest_wl = np.max(wavelengths[peaks])
            strongest_wl = wavelengths[peaks][np.argmax(intensities[peaks])]
            print(f"Highest Emitted Wavelength: {highest_wl:.2f} nm")
            print(f"Strongest Intensity Wavelength: {strongest_wl:.2f} nm\n")
            
            # Step D: Save a graph for this eclipse
            plt.figure(figsize=(10, 4))
            plt.plot(wavelengths, intensities, color="navy", linewidth=1, label="Solar Spectrum")
            plt.scatter(wavelengths[peaks], intensities[peaks], color="orange", zorder=5, label="Peaks")
            plt.axvline(highest_wl, color="green", linestyle="--", label=f"Highest WL: {highest_wl:.1f} nm")
            plt.title(f"Solar Emission Spectrum - {date_str}")
            plt.xlabel("Wavelength (nm)")
            plt.ylabel("Irradiance (W/m^2/nm)")
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.savefig(f"{label}_plot.png", dpi=150)
            plt.close()
        else:
            print("No peaks detected above threshold.\n")
            
    except Exception as e:
        print(f"Error processing {date_str}: {e}\n")
