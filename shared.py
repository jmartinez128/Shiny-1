from pathlib import Path

import pandas as pd

app_dir = Path(__file__).parent
shopping_trends = pd.read_csv(app_dir / "shopping_trends.csv")
