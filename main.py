import urllib.request
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# Exact dates of the last 3 solar eclipses
eclipse_dates = {
    "2025-09-21_partial": "2025-09-21",
    "2026-02-17_annular": "2026-02-17",
    "2026-08-12_total":   "2026-08-12"
}

# NOAA NCEI / LISIRD TSIS-1 Daily Solar Spectral Irradiance endpoint
base_url = "https://colorado.edu"

for label, date_str in eclipse_dates.items():
    # Use proper URL encoding for >= and <= operators
    query_url = f"{base_url}?time%3E={date_str}T00:00:00Z&time%3C={date_str}T23:59:59Z"
    csv_filename = f"{label}_spectrum.csv"
    
    print(f"--- Processing {label} ({date_str}) ---")
    try:
        # Add User-Agent header so NASA/LASP server accepts the request
        req = urllib.request.Request(query_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as response, open(csv_filename, "wb") as out_file:
            out_file.write(response.read())
            
        # Check if the server returned HTML instead of CSV
        with open(csv_filename, "r", encoding="utf-8", errors="ignore") as f:
            first_line = f.readline().strip()
            if first_line.startswith("<") or "html" in first_line.lower():
                print(f"Server returned webpage instead of CSV for {date_str}. First line: {first_line}\n")
                continue

        # Read CSV safely, skipping malformed lines if any exist
        df = pd.read_csv(csv_filename, on_bad_lines="skip")
        print("Columns found:", df.columns.tolist())
        
        # Find wavelength and irradiance columns automatically
        wl_cols = [c for c in df.columns if "wavelength" in c.lower()]
        int_cols = [c for c in df.columns if "irradiance" in c.lower()]
        
        if not wl_cols or not int_cols:
            print(f"Could not find wavelength/irradiance columns. Preview:\n{df.head(2)}\n")
            continue
            
        wavelengths = pd.to_numeric(df[wl_cols[0]], errors="coerce").to_numpy()
        intensities = pd.to_numeric(df[int_cols[0]], errors="coerce").to_numpy()
        
        # Clean invalid rows
        valid = ~np.isnan(wavelengths) & ~np.isnan(intensities)
        wavelengths = wavelengths[valid]
        intensities = intensities[valid]
        
        if len(wavelengths) == 0:
            print(f"No valid numerical data rows for {date_str}.\n")
            continue

        # Estimate noise floor and detect peaks
        baseline = np.median(intensities)
        noise_std = 1.4826 * np.median(np.abs(intensities - baseline))
        threshold = baseline + (3.0 * noise_std)
        
        peaks, _ = find_peaks(intensities, height=threshold, prominence=noise_std)
        
        if len(peaks) > 0:
            highest_wl = np.max(wavelengths[peaks])
            strongest_wl = wavelengths[peaks][np.argmax(intensities[peaks])]
            print(f"SUCCESS -> Highest Emitted Wavelength: {highest_wl:.2f} nm")
            print(f"SUCCESS -> Strongest Intensity Wavelength: {strongest_wl:.2f} nm\n")
            
            # Save graph
            plt.figure(figsize=(10, 4))
            plt.plot(wavelengths, intensities, color="navy", linewidth=1, label="Solar Spectrum")
            plt.scatter(wavelengths[peaks], intensities[peaks], color="orange", zorder=5, label="Detected Peaks")
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
        print(f"Error on {date_str}: {e}\n")
