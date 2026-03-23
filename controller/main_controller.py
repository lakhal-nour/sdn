import yaml
import os
import sys

CONFIG_PATH = "/app/iac/controller_config.yml"

try:
    with open(CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)

    apps = config["controller"]["apps"]

    # flush=True force l'affichage immédiat dans les logs Docker
    print(f"🚀 Lancement du contrôleur Ryu avec : {apps}", flush=True)

    # os.execvp remplace le processus Python par Ryu (Meilleure pratique Docker)
    os.execvp("ryu-manager", ["ryu-manager", "--verbose"] + apps)

except Exception as e:
    print(f"❌ Erreur : {e}")
    sys.exit(1)