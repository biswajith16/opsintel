"""Phase 2 validates deterministic Isolation Forest inputs; artifact persistence follows the production repository adapter."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "apps/api"))
from app.ml.scoring import isolation_forest_scores
print({"model":"IsolationForest","seed":20260828,"scores":isolation_forest_scores([(70,2,110),(71,2.2,108),(92,8.4,42),(69,1.8,115),(70,2.1,112)])})
