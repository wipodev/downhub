import os
import json
from crx3 import creator, verifier

EXT_FOLDER = "extension"
KEYS_FOLDER = "keys"
PRIVATE_KEY = os.path.join(KEYS_FOLDER, "DownHub.pem")
TEMP_CRX = os.path.join(KEYS_FOLDER, "temp.crx")
MANIFEST = os.path.join(EXT_FOLDER, "manifest.json")
NATIVE_REGISTRY = "net.wipodev.downhub"

def injectKey(file, key, keyValue):
    if not os.path.exists(file):
        print(f"⚠️ Warning: {file} not found. Skipping injection.")
        return
    with open(file, "r", encoding="utf-8") as f:
        newFile = json.load(f)
    newFile[key] = keyValue
    with open(file, "w", encoding="utf-8") as f:
        json.dump(newFile, f, indent=2, ensure_ascii=False)


# 1. Crear clave privada si no existe
if not os.path.exists(PRIVATE_KEY):
    os.makedirs(KEYS_FOLDER, exist_ok=True)
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
injectKey(MANIFEST, "key", pub_key)
print("✅ Manifest.json updated with public key.")

# 4. Reemplazar ID en native registry
injectKey(NATIVE_REGISTRY, "allowed_origins", [f"chrome-extension://{ext_id}/"])
print(f"✅ native registry updated with chrome-extension://{ext_id}")

# 5. Limpiar crx temporal
if os.path.exists(TEMP_CRX):
    os.remove(TEMP_CRX)
