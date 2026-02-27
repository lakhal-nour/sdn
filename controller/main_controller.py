import yaml
import subprocess

CONFIG_PATH = "/app/iac/controller_config.yml"

with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

app_string = config["controller"]["app"]
print(f"🚀 Lancement du contrôleur Ryu avec : {app_string}")

# On sépare la chaîne en une liste d'arguments pour subprocess
cmd = ["ryu-manager"] + app_string.split()
subprocess.run(cmd)
