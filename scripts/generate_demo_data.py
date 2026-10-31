from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from gridtwin.demo_data import make_synthetic_load

out = Path(__file__).resolve().parents[1] / "data" / "synthetic_hourly_load.csv"
make_synthetic_load().to_csv(out, index=False)
print(f"Wrote synthetic demo data: {out}")
