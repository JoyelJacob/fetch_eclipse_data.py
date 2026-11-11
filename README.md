# fetch_eclipse_data.py
To connect directly to NREL / NASA ASTM G-173 Solar Spectral Irradiance API and download the exact wavelength-vs-irradiance data files for the solar eclipses on September 21, 2025, February 17, 2026, and August 12, 2026

To find the highest emitted Wavelength during the solar eclipses 

# Solar Eclipse Wavelength Extractor

A Python signal-processing tool that analyzes solar emission spectra during a solar eclipse to isolate emission peaks above background noise and extract the **highest (longest) emitted wavelength** alongside the **strongest peak intensity wavelength**.

## Dataset Used
* **Primary Attempt:** Fetches standard reference solar spectral irradiance data (NREL / NASA ASTM G-173) when external network access is available.
* **Built-In Coronal Simulation (`solar_spectrum_data.csv`):** When running offline or in restricted environments, the script generates a calibrated solar corona emission profile modeled on real astrophysical spectral lines documented by NASA and solar observatories:
  * **Fe XIV (530.3 nm):** Coronal green emission line
  * **Fe X (637.4 nm):** Coronal red emission line
  * **Fe XIII (1074.7 nm):** Coronal near-infrared emission line
* **Custom Eclipse Data Ready:** Supports uploading any external `.csv` file (such as ground-based spectrometer logs from Zenodo or irradiance tables from NASA POWER).

## Key Features
* **Noise Floor Estimation:** Uses Median Absolute Deviation (MAD) to separate genuine coronal emission lines from background noise.
* **Peak Detection:** Applies `scipy.signal.find_peaks` with prominence filtering to locate spectral emission lines.
* **Automated Visualization:** Generates annotated spectrum plots highlighting all detected peaks and the longest emitted wavelength.

## Sample Output
![Solar Eclipse Emission Spectrum](eclipse_result.png)

* **Highest (Longest) Emitted Wavelength:** `1074.48 nm`
* **Strongest Peak Intensity Wavelength:** `530.12 nm`

## How to Run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the analysis script:
   ```bash
   python main.py
   ```
