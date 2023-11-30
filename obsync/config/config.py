import os
import random
import pickle
from pathlib import Path
import yaml


Secret = None

SecretPath = "secret.gob"
Host = "localhost:3000"
DataDir = "."
SignUpKey = ""
MaxStorageBytes = 10 * 1073741824  # 10 GB
MaxSitesPerUser = 5

SecretPath = os.path.join(DataDir, "secret.gob")


def init():
    global SecretPath, Host, DataDir, Secret, SignUpKey, MaxStorageBytes, MaxSitesPerUser

    config_file_path = os.path.join(Path(__file__).parent.parent, "config.yml")
    with open(config_file_path, "r") as file:
        config = yaml.safe_load(file)

    Host, SignUpKey, DataDir, MaxStorageBytes, MaxSitesPerUser = (
        config.get("HOST", "localhost:3000"),
        config.get("SIGNUP_KEY", ""),
        config.get("DATA_DIR", "."),
        int(config.get("MAX_STORAGE_GB", 10)) * 1073741824,
        int(config.get("MAX_SITES_PER_USER", 5)),
    )

    Path(DataDir).mkdir(parents=True, exist_ok=True)
    SecretPath = os.path.join(DataDir, "secret.gob")

    if not os.path.exists(SecretPath):
        Secret = random.randbytes(64)
        with open(SecretPath, "wb") as f:
            pickle.dump(Secret, f)
    else:
        with open(SecretPath, "rb") as f:
            Secret = pickle.load(f)


init()
