import csv
import os
from typing import Dict, List, Set
from datetime import datetime

# Pour parser les CSV qui sont enregistrés
def parse_csv_file(filepath: str) -> Dict[str, Set[str]]:
    stores = {}
    
    with open(filepath, "r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader, None)
        
        if header is None:
            return {}
        
        for row in reader:
            if len(row) >= 2:
                store_name = row[0].strip()
                brands_str = row[1].strip()
                
                brands = {brand.strip() for brand in brands_str.split(";") if brand.strip()}
                stores[store_name] = brands
    
    return stores

# Pour comparter les deux fichiers CSV et identifier les changements
def compare_csv_files(old_file: str, new_file: str) -> Dict:
    old_stores = parse_csv_file(old_file)
    new_stores = parse_csv_file(new_file)
    
    results = {
        "stores": {},
        "summary": {
            "stores_disappeared": [],
            "stores_appeared": [],
            "stores_changed": 0,
            "stores_unchanged": 0
        }
    }
    
    for store_name, old_brands in old_stores.items():
        new_brands = new_stores.get(store_name, set())
        
        added = new_brands - old_brands
        removed = old_brands - new_brands
        
        if added or removed or not new_brands:
            results["stores"][store_name] = {
                "added": list(added),
                "removed": list(removed),
                "old_count": len(old_brands),
                "new_count": len(new_brands),
                "status": "disappeared" if len(new_brands) == 0 and len(old_brands) > 0 else "changed"
            }
            if added or removed:
                results["summary"]["stores_changed"] += 1
        else:
            results["summary"]["stores_unchanged"] += 1
            results["stores"][store_name] = {
                "added": [],
                "removed": [],
                "old_count": len(old_brands),
                "new_count": len(new_brands),
                "status": "unchanged"
            }
    
    # On regarder si il y a de nouvelle boutique
    for store_name, new_brands in new_stores.items():
        if store_name not in old_stores:
            results["stores"][store_name] = {
                "added": list(new_brands),
                "removed": [],
                "old_count": 0,
                "new_count": len(new_brands),
                "status": "appeared"
            }
            results["summary"]["stores_appeared"].append(store_name)
    
    # On regarde si des boutiques on disparue
    for store_name in old_stores:
        if store_name not in new_stores:
            results["summary"]["stores_disappeared"].append(store_name)
    
    return results

def export_comparison_to_json(results: Dict, output_file: str = "comparison_report.json") -> None:
    import json
    
    json_results = {
        "stores": {},
        "summary": results["summary"]
    }
    
    for store, changes in results["stores"].items():
        json_results["stores"][store] = {
            "added": sorted(changes["added"]),
            "removed": sorted(changes["removed"]),
            "old_count": changes["old_count"],
            "new_count": changes["new_count"],
            "status": changes["status"]
        }
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(json_results, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Rapport exporté dans {output_file}")

# Pour avoir la liste des fichiers CSV dans le bon ordre
def get_all_timestamped_files() -> List[str]:
    files = [f for f in os.listdir(".") if f.startswith("boutiques_") and f.endswith(".csv")]
    return sorted(files)

# On génère le fichier avec toutes les comparaisons
def generate_history() -> List[str]:
    files = get_all_timestamped_files()
    
    if len(files) < 2:
        return []
    
    all_changes = []
    
    for i in range(len(files) - 1):
        old_file = files[i]
        new_file = files[i + 1]
        results = compare_csv_files(old_file, new_file)
        
        for store, changes in results["stores"].items():
            for brand in changes["removed"]:
                all_changes.append(f"La marque {brand} est partie du magasin de {store}")
            
            for brand in changes["added"]:
                all_changes.append(f"La marque {brand} est arrivee au magasin de {store}")
    
    return all_changes

# La fonction qui est appelé pour checker et sauvegarder le tout au format txt
def save_changes_to_txt(output_file: str = None) -> str:
    if output_file is None:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_file = f"changes_{timestamp}.txt"
    
    changes = generate_history()
    
    with open(output_file, "w", encoding="utf-8") as f:
        for change in changes:
            f.write(change + "\n")
    
    print(f"Changements sauvegardés dans {output_file} ({len(changes)} changements)")
    return output_file

if __name__ == "__main__":
    
    files = get_all_timestamped_files()
    
    print(f"Fichiers trouvés: {len(files)}")
    
    output_file = save_changes_to_txt()
    print(f"Rapport complet des changements sauvegardé dans {output_file}")

