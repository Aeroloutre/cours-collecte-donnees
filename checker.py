import csv
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple
from datetime import datetime


def parse_csv_file(filepath: str) -> Dict[str, Set[str]]:
    """Parse a CSV file and return a dictionary of stores with their brands as sets."""
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


def compare_csv_files(old_file: str, new_file: str) -> Dict:
    """Compare two CSV files and return detailed changes."""
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
    
    # Check for new stores
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
    
    # Identify disappeared stores
    for store_name in old_stores:
        if store_name not in new_stores:
            results["summary"]["stores_disappeared"].append(store_name)
    
    return results


def export_comparison_to_json(results: Dict, output_file: str = "comparison_report.json") -> None:
    """Export comparison results to JSON format."""
    import json
    
    # Convert sets to lists for JSON serialization
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


def get_all_timestamped_files() -> List[str]:
    """Get all timestamped CSV files sorted chronologically."""
    files = [f for f in os.listdir(".") if f.startswith("boutiques_") and f.endswith(".csv")]
    return sorted(files)


def generate_history() -> List[str]:
    """Generate a list of all brand changes across all CSV files in chronological order."""
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


def save_changes_to_txt(output_file: str = None) -> str:
    """Generate all changes and save them to a timestamped .txt file. Returns the filename."""
    if output_file is None:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_file = f"changes_{timestamp}.txt"
    
    changes = generate_history()
    
    with open(output_file, "w", encoding="utf-8") as f:
        for change in changes:
            f.write(change + "\n")
    
    print(f"✓ Changements sauvegardés dans {output_file} ({len(changes)} changements)")
    return output_file


def display_history() -> None:
    """Display all changes in the console."""
    changes = generate_history()
    
    if not changes:
        print("Aucun changement")
        return
    
    print("\nHistorique des changements de marques:\n")
    for change in changes:
        print(change)


if __name__ == "__main__":
    print("=" * 70)
    print("VÉRIFICATION MULTI-FICHIERS - CHECKER")
    print("=" * 70)
    
    files = get_all_timestamped_files()
    
    if len(files) < 2:
        print("\n⚠ Pas assez de fichiers CSV pour effectuer une comparaison.")
        print(f"  Fichiers trouvés: {len(files)}")
        exit(1)
    
    print(f"\n✓ {len(files)} fichiers CSV détectés\n")
    
    # Generate and save changes to txt file
    output_file = save_changes_to_txt()
    
    # Also display in console
    print("\nAperçu des changements:")
    display_history()

