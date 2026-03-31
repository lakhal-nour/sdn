FROM python:3.9

WORKDIR /app

RUN pip install "setuptools<59.6.0"
RUN pip install ryu eventlet==0.30.2 tinyrpc pyyaml requests

# Patch de qos_simple_switch_13 pour utiliser table_id=1
RUN python3 - <<'PY'
from pathlib import Path
import ryu

base = Path(ryu.__file__).resolve().parent / "app"
src = base / "simple_switch_13.py"
dst = base / "qos_simple_switch_13.py"

content = src.read_text(encoding="utf-8")
content = content.replace(
    "mod = parser.OFPFlowMod(datapath=datapath, priority=priority,",
    "mod = parser.OFPFlowMod(datapath=datapath, priority=priority, table_id=1,"
)
dst.write_text(content, encoding="utf-8")
print(f"Generated {dst}")
PY

COPY . /app

EXPOSE 6653 8080

CMD ["python3", "controller/main_controller.py"]