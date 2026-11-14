import os
import json
import zipfile
import re
import shutil
from datetime import datetime

def extract_metadata(ipa_path):
    filename = os.path.splitext(os.path.basename(ipa_path))[0]
    bundle_id = f"com.custom.{filename.lower().replace(' ', '')}"
    version = "1.0.0"
    display_name = filename
    
    temp_dir = f"extracted_{filename}"
    
    try:
        with zipfile.ZipFile(ipa_path, 'r') as ipa:
            ipa.extractall(temp_dir)
            
        plist_path = None
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file == "Info.plist" and "Payload" in root:
                    plist_path = os.path.join(root, file)
                    break
            if plist_path:
                break
                
        if plist_path:
            with open(plist_path, 'rb') as f:
                plist_data = f.read()
            
            plist_str = plist_data.decode('utf-8', errors='ignore')
            
            bid_match = re.search(r'<key>CFBundleIdentifier</key>\s*<string>([^<]+)</string>', plist_str)
            ver_match = re.search(r'<key>CFBundleShortVersionString</key>\s*<string>([^<]+)</string>', plist_str)
            name_match = re.search(r'<key>CFBundleDisplayName</key>\s*<string>([^<]+)</string>', plist_str)
            
            if not name_match:
                name_match = re.search(r'<key>CFBundleName</key>\s*<string>([^<]+)</string>', plist_str)
            
            if bid_match: bundle_id = bid_match.group(1).strip()
            if ver_match: version = ver_match.group(1).strip()
            if name_match: display_name = name_match.group(1).strip()
            
    except Exception as e:
        print(f"Extraction processing note for {ipa_path}: {e}")
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        
    return bundle_id, version, display_name

def main():
    username = "TTVNerdWord"
    repo_name = "Armor-Sandbox-Tweaks"
    base_url = f"https://{username}.github.io/{repo_name}"
    
    data = {
        "name": "Armor Sandbox Tweaks",
        "identifier": "com.ArmorSandbox.repo",
        "subtitle": "I do what I want. I do what I please",
        "iconURL": "https://raw.githubusercontent.com/TTVNerdWord/NW-Repo-IG/main/hi.png",
        "tintColor": "#007AFF",
        "apps": [],
        "news": []
    }

    found_ipas = False
    apps_dict = {}  # Dictionary to group versions by bundleIdentifier

    for file in os.listdir("."):
        if file.endswith(".ipa"):
            found_ipas = True
            bundle_id, version, display_name = extract_metadata(file)
            file_size = os.path.getsize(file)
            current_date = datetime.utcnow().strftime("%Y-%m-%d")
            
            version_entry = {
                "version": version,
                "date": current_date,
                "downloadURL": f"{base_url}/{file}",
                "size": file_size,
                "localizedDescription": f"Version {version} release update."
            }
            
            if bundle_id in apps_dict:
                # If app already exists, append this version to its list
                apps_dict[bundle_id]["versions"].append(version_entry)
            else:
                # Otherwise, create the new app entry with this version
                apps_dict[bundle_id] = {
                    "name": display_name,
                    "bundleIdentifier": bundle_id,
                    "developerName": "Self-Published",
                    "subtitle": "Sideloaded Build",
                    "localizedDescription": f"Sideloaded build for {display_name} compiled dynamically.",
                    "iconURL": "https://raw.githubusercontent.com/TTVNerdWord/NW-Repo-IG/main/hi.png",
                    "tintColor": "#007AFF",
                    "versions": [version_entry]
                }
            
            print(f"Successfully processed: {display_name} [{bundle_id}] v{version}")

    if not found_ipas:
        print("No .ipa files detected in the root directory.")

    # Convert the grouped dictionary back into the apps list
    data["apps"] = list(apps_dict.values())

    with open("apps.json", "w") as f:
        json.dump(data, f, indent=2)
        
    with open("apps_esign.json", "w") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    main()
