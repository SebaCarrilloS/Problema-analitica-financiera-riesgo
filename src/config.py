from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
SYNTHETIC_DATA_DIR = DATA_DIR / "synthetic"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
DATABASE_DIR = DATA_DIR / "database"
EXPORTS_DIR = DATA_DIR / "exports"

HOME_CREDIT_RAW_DIR = RAW_DATA_DIR / "home_credit"
CORPORATE_SYNTHETIC_DIR = SYNTHETIC_DATA_DIR / "corporate"

DATABASE_PATH = DATABASE_DIR / "financiera.duckdb"