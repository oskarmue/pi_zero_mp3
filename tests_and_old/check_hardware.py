import os

def check_hardware():
    model_path = '/proc/device-tree/model'
    if os.path.exists(model_path):
        with open(model_path, 'r') as f:
            model = f.read().lower()
            if 'raspberry pi' in model:
                return "Raspberry Pi"
    return "Laptop / PC"

print(f"Das Skript läuft auf: {check_hardware()}")