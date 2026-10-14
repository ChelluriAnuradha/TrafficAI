# TrafficAI — Traffic Congestion Pattern Mining System

## Run locally (Windows / VS Code)

1. Install Python 3.10 or newer if not already installed.
2. Open this project folder in VS Code.
3. Open Terminal > New Terminal.
4. Create a virtual environment (optional but recommended):
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
5. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
6. Run data mining:
   ```powershell
   python data_mining.py
   ```
7. Start the backend:
   ```powershell
   python app.py
   ```
8. Open http://127.0.0.1:5000 in your browser.

If PowerShell blocks virtual-environment activation, skip steps 4's activation command and run `python -m pip install -r requirements.txt` directly.

## Backend API
- `GET /api/health` — check server
- `GET /api/stats` — dataset summary
- `GET /api/data` — CSV data for charts
- `GET /api/patterns` — category counts and top cities
- `GET /api/reports.csv` — download a CSV report
- `POST /api/predict` — baseline rule-based congestion estimate

## Important project limitation
The supplied dataset is city-level data (`City`, `AverageTCI`, `MaxTCI`, and `CongestionLevel`). It does not contain timestamped traffic, weather, or vehicle-count training records. The prediction endpoint is therefore a transparent rule-based baseline, not a trained machine-learning model. The UI's weather/time/vehicle inputs are user inputs to that baseline, not fields learned from the city dataset.
