import os
import json
from crx3 import creator, verifier

EXT_FOLDER = "extension"
KEYS_FOLDER = "keys"
PRIVATE_KEY = os.path.join(KEYS_FOLDER, "DownHub.pem")
TEMP_CRX = os.path.join(KEYS_FOLDER, "temp.crx")
MANIFEST = os.path.join(EXT_FOLDER, "manifest.json")
MAIN_API = os.path.join("api", "main.py")

os.makedirs(KEYS_FOLDER, exist_ok=True)

# 1. Crear clave privada si no existe
if not os.path.exists(PRIVATE_KEY):
    creator.create_private_key_file(PRIVATE_KEY)
    print("✅ Private key generated:", PRIVATE_KEY)

# 2. Crear crx temporal y verificar
creator.create_crx_file(EXT_FOLDER, PRIVATE_KEY, TEMP_CRX)
verifier_result, header_info = verifier.verify(TEMP_CRX)

if verifier_result != verifier.VerifierResult.OK_FULL:
    raise RuntimeError("❌ Could not verify CRX.")

ext_id = header_info.crx_id
pub_key = header_info.public_key
print("✅ Extension ID:", ext_id)

# 3. Insertar clave en manifest.json
with open(MANIFEST, "r", encoding="utf-8") as f:
    manifest = json.load(f)

manifest["key"] = pub_key

with open(MANIFEST, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)

print("✅ Manifest.json updated with public key.")

# 4. Reemplazar ID en api/main.py (allow_origins)
with open(MAIN_API, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if "chrome-extension://" in line:
        new_lines.append(f'        "chrome-extension://{ext_id}",\n')
    else:
        new_lines.append(line)

with open(MAIN_API, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print(f"✅ api/main.py updated with chrome-extension://{ext_id}")

# 5. Limpiar crx temporal
if os.path.exists(TEMP_CRX):
    os.remove(TEMP_CRX)
