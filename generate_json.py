import os
import json
import zipfile
import re
from datetime import datetime

def extract_metadata(ipa_path):
    bundle_id = "com.example.unknown"
    version = "1.0.0"
    display_name = os.path.splitext(os.path.basename(ipa_path))[0]
    
    try:
        with zipfile.ZipFile(ipa_path, 'r') as ipa:
            # Look for Info.plist inside the Payload directory
            plist_path = None
            for file in ipa.namelist():
                if re.match(r'Payload/[^/]+\.app/Info.plist$', file):
                    plist_path = file
                    break
            
            if plist_path:
                plist_data = ipa.read(plist_path)
                # Fallback simple string extraction for Linux environments
                plist_str = plist_data.decode('utf-8', errors='ignore')
                
                bid_match = re.search(r'<key>CFBundleIdentifier</key>\s*<string>([^<]+)</string>', plist_str)
                ver_match = re.search(r'<key>CFBundleShortVersionString</key>\s*<string>([^<]+)</string>', plist_str)
                name_match = re.search(r'<key>CFBundleDisplayName</key>\s*<string>([^<]+)</string>', plist_str)
                
                if bid_match: bundle_id = bid_match.group(1).strip()
                if ver_match: version = ver_match.group(1).strip()
                if name_match: display_name = name_match.group(1).strip()
    except Exception as e:
        print(f"Warning extraction failed for {ipa_path}: {e}")
        
    return bundle_id, version, display_name

def main():
    username = "TTVNerdWord"
    repo_name = "NW-Repo-IG"
    base_url = f"https://{username}.github.io/{repo_name}"
    
    # Load existing or fallback structure
    if os.path.exists("apps.json") and os.path.getsize("apps.json") > 0:
        try:
            with open("apps.json", "r") as f:
                data = json.load(f)
        except:
            data = {"name": "NW-Repo-IG", "identifier": "com.ttvnerdword.repo", "apps": []}
    else:
        data = {"name": "NW-Repo-IG", "identifier": "com.ttvnerdword.repo", "apps": []}
        
    data["apps"] = [] # Reset list to compile fresh
    
    # Scan root directory for IPAs
    for file in os.listdir("."):
        if file.endswith(".ipa"):
            bundle_id, version, display_name = extract_metadata(file)
            
            app_entry = {
                "name": display_name,
                "bundleIdentifier": bundle_id,
                "developerName": "TTVNerdWord",
                "version": version,
                "versionDate": datetime.utcnow().strftime("%Y-%m-%d"),
                "downloadURL": f"{base_url}/{file}",
                "localizedDescription": f"Automatically generated source tracking for {display_name}."
            }
            data["apps"].append(app_entry)
            print(f"Processed: {display_name} ({bundle_id}) v{version}")

    with open("apps.json", "w") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    main()
