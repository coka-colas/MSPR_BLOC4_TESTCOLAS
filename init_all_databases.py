#!/usr/bin/env python3
"""
Script principal d'initialisation de toutes les bases de données
à partir des fichiers JSON fournis
"""

import subprocess
import sys
from pathlib import Path

def run_script(script_path, description):
    """Exécuter un script d'initialisation"""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([
            sys.executable, str(script_path)
        ], capture_output=True, text=True, cwd=script_path.parent)
        
        if result.returncode == 0:
            print(result.stdout)
            print(f"✅ {description} - SUCCÈS")
            return True
        else:
            print(f"❌ {description} - ÉCHEC")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution de {script_path}: {e}")
        return False

def main():
    """Script principal"""
    print("🚀 INITIALISATION DE TOUTES LES BASES DE DONNÉES")
    print("📁 Utilisation des fichiers JSON pour peupler les bases")
    
    base_dir = Path(__file__).parent
    success_count = 0
    total_count = 3
    
    # Scripts d'initialisation dans l'ordre
    scripts = [
        (base_dir / "API_Produits" / "init_products_db.py", "Initialisation base de données PRODUITS"),
        (base_dir / "API_Clients" / "init_clients_db.py", "Initialisation base de données CLIENTS"),
        (base_dir / "API_Commandes" / "init_orders_db.py", "Initialisation base de données COMMANDES")
    ]
    
    # Exécuter chaque script
    for script_path, description in scripts:
        if script_path.exists():
            if run_script(script_path, description):
                success_count += 1
        else:
            print(f"❌ Script non trouvé: {script_path}")
    
    # Résumé final
    print(f"\n{'='*60}")
    print(f"📊 RÉSUMÉ FINAL")
    print(f"{'='*60}")
    print(f"✅ Scripts réussis: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("🎉 TOUTES LES BASES DE DONNÉES ONT ÉTÉ INITIALISÉES AVEC SUCCÈS!")
        print()
        print("📋 Données disponibles:")
        print("  - API_Produits (port 8001): Catalogue de produits avec prix et stocks")
        print("  - API_Clients (port 8002): Base de clients avec profils et adresses")
        print("  - API_Commandes (port 8000): Commandes avec relations clients-produits")
        print()
        print("🔧 Pour démarrer les services:")
        print("  docker-compose up --build -d")
        print()
        print("🌐 Endpoints disponibles:")
        print("  - http://localhost:8000/docs (API Commandes)")
        print("  - http://localhost:8001/docs (API Produits)")
        print("  - http://localhost:8002/docs (API Clients)")
    else:
        print(f"⚠️  {total_count - success_count} script(s) ont échoué")
        print("Vérifiez les erreurs ci-dessus et relancez les scripts individuellement si nécessaire")

if __name__ == "__main__":
    main()