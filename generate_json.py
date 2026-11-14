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
    
 
    icon_url = f"https://raw.githubusercontent.com/{username}/{repo_name}/main/Images/AS.png"
    icon_url2 = f"https://raw.githubusercontent.com/{username}/{repo_name}/main/Images/Hi.png" 
    
    data = {
        "name": "Armor Sandbox Tweaks",
        "identifier": "com.ArmorSandbox.repo",
        "subtitle": "I do what I want. I do what I please",
        "iconURL": icon_url2,
        "tintColor": "#007AFF",
        "apps": [],
        "news": []
    }

    found_ipas = False
    ipa_dir = "IPAs"

    if os.path.exists(ipa_dir) and os.path.isdir(ipa_dir):
        for file in os.listdir(ipa_dir):
            if file.endswith(".ipa"):
                found_ipas = True
                ipa_path = os.path.join(ipa_dir, file)
                plist_bundle_id, version, display_name = extract_metadata(ipa_path)
                file_size = os.path.getsize(ipa_path)
                current_date = datetime.utcnow().strftime("%Y-%m-%d")
                
                # Create a unique bundle ID suffix so multiple uploads don't conflict
                file_slug = os.path.splitext(file)[0].lower()
                file_slug = re.sub(r'[^a-z0-9]', '', file_slug)
                
                unique_bundle_id = f"{plist_bundle_id}.{file_slug}"
                unique_app_name = f"{display_name} ({version})"
                
                app_entry = {
                    "name": unique_app_name,
                    "bundleIdentifier": unique_bundle_id,
                    "developerName": "Self-Published",
                    "subtitle": "Sideloaded Build",
                    "localizedDescription": f"Sideloaded build for {unique_app_name} compiled dynamically.",
                    "iconURL": icon_url,
                    "tintColor": "#007AFF",
                    "versions": [
                        {
                            "version": version,
                            "date": current_date,
                            "downloadURL": f"{base_url}/IPAs/{file}",
                            "size": file_size,
                            "localizedDescription": f"Version {version} release update."
                        }
                    ]
                }
                data["apps"].append(app_entry)
                print(f"Successfully processed: {unique_app_name} [{unique_bundle_id}]")

    if not found_ipas:
        print("No .ipa files detected in the 'IPAs' directory.")

    with open("apps.json", "w") as f:
        json.dump(data, f, indent=2)
        
    with open("apps_esign.json", "w") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    main()
