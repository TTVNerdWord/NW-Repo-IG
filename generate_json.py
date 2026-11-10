import os
import json
import zipfile
import re
from datetime import datetime

def extract_metadata(ipa_path):
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
        print(f"Extraction note: {e}")
        
    return bundle_id, version, display_name

def main():
    username = "TTVNerdWord"
    repo_name = "NW-Repo-IG"
    
    # Assembling chunks cleanly inside the automation script
    base_url = f"https://{username}.github.io/{repo_name}"
    
    # SideStore explicitly demands subtitle, iconURL, and tintColor layouts
    data = {
        "name": "NW Repository",
        "identifier": "com.ttvnerdword.repo",
        "subtitle": "Custom Sideload Apps",
        "iconURL": "https://githubusercontent.com",
        "tintColor": "#007AFF",
        "apps": []
    }
    
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
                "localizedDescription": f"Sideloaded build for {display_name}.",
                "iconURL": "https://githubusercontent.com",
                "size": os.path.getsize(file)
            }
            data["apps"].append(app_entry)
            print(f"Successfully formatted: {display_name}")

    with open("apps.json", "w") as f:
        json.dump(data, f, indent=2)
        
    with open("apps_esign.json", "w") as f:
        json.dump(data, f, indent=2)
        
    if not os.path.exists("bundleId.csv"):
        with open("bundleId.csv", "w") as f:
            f.write("Source,BundleId\n")

if __name__ == "__main__":
    main()
