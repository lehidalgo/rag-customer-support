from utils.config_loader import load_config

# Load the database configuration
db_config = load_config("configs/database_config.yaml")

# Access configuration parameters
db_host = db_config["database"]["host"]
db_port = db_config["database"]["port"]
