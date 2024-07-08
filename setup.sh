mkdir batch_in
mkdir batch_out

python3 -m venv .venv
. .venv/bin/activate
pip3 install -r requirements.txt
python3 process.py
deactivate
