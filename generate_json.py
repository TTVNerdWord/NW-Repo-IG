import os
import json
import zipfile
import re
from datetime import datetime

def extract_metadata(ipa_path):
    # Set proper defaults for your specific app
    bundle_id = "com.johncoates.ArmorSandbox"
    version = "2.0.0"
    display_name = "ArmorSandbox"
    
    try:
        with zipfile.ZipFile(ipa_path, 'r') as ipa:
            plist_path = None
            for file in ipa.namelist():
                if re.match(r'Payload/[^/]+\.app/Info.plist$', file):
                    plist_path = file
                    break
            
            if plist_path:
                plist_data = ipa.read(plist_path)
                plist_str = plist_data.decode('utf-8', errors='ignore')
                
                bid_match = re.search(r'<key>CFBundleIdentifier</key>\s*<string>([^<]+)</string>', plist_str)
                ver_match = re.search(r'<key>CFBundleShortVersionString</key>\s*<string>([^<]+)</string>', plist_str)
                name_match = re.search(r'<key>CFBundleDisplayName</key>\s*<string>([^<]+)</string>', plist_str)
                
                if bid_match: bundle_id = bid_match.group(1).strip()
                if ver_match: version = ver_match.group(1).strip()
                if name_match: display_name = name_match.group(1).strip()
    except Exception as e:
        print(f"Extraction note for {ipa_path}: {e}")
        
    return bundle_id, version, display_name

def main():
    username = "TTVNerdWord"
    repo_name = "NW-Repo-IG"
    base_url = f"https://{username}.github.io/{repo_name}"
    
    # Force initialize clean structure to eliminate previous 404/corruption states
    data = {
        "name": "NW-Repo-IG",
        "identifier": "com.ttvnerdword.repo",
        "apps": []
    }
    
    # Process local IPA files sitting right in your repo
    found_ipas = False
    for file in os.listdir("."):
        if file.endswith(".ipa"):
            found_ipas = True
            bundle_id, version, display_name = extract_metadata(file)
            
            app_entry = {
                "name": display_name,
                "bundleIdentifier": bundle_id,
                "developerName": "TTVNerdWord",
                "version": version,
                "versionDate": datetime.utcnow().strftime("%Y-%m-%d"),
                "downloadURL": f"{base_url}/{file}",
                "localizedDescription": f"Sideloaded build for {display_name}."
            }
            data["apps"].append(app_entry)
            print(f"Successfully processed: {display_name}")

    if not found_ipas:
        print("Note: No .ipa files found in root directory to process.")

    # Write out the clean JSON file cleanly
    with open("apps.json", "w") as f:
        json.dump(data, f, indent=2)
        
    # Create empty fallbacks for other files the .yml tracking pattern expects
    with open("apps_esign.json", "w") as f:
        json.dump(data, f, indent=2)
        
    if not os.path.exists("bundleId.csv"):
        with open("bundleId.csv", "w") as f:
            f.write("Source,BundleId\n")

if __name__ == "__main__":
    main()
