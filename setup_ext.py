from crx3 import creator, verifier

extension_folder = 'extension'
extension = 'dist/DownTube.crx'
private_key = 'dist/DounTube.pem'

creator.create_private_key_file(private_key)

creator.create_crx_file(extension_folder, private_key, extension)

verifier_result, header_info = verifier.verify(extension)

if verifier_result == verifier.VerifierResult.OK_FULL:
    print("The .crx file is valid.")
    print("Extension ID:", header_info.crx_id)
    print("Public key:", header_info.public_key)
else:
    print("The .crx file is invalid.")