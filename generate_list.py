# python pb_model_review\generate_list.py
import os
import json
import pandas as pd  # NYTT: Importerar pandas för att läsa CSV-filen

# Sökväg till huvudmappen som innehåller alla 'run' undermappar.
BASE_REPORTS_PATH = 'pb_model_review/Fish'

# NYTT: Sökväg till CSV-filen med artnamn.
SPECIES_NAMES_CSV = 'pb_model_review/species_names.csv'

# Namn på filen som kommer innehålla vår data.
OUTPUT_JS_FILE = 'pb_model_review/reports_data.js'

def generate_reports_data():
    """
    Skannar alla undermappar i BASE_REPORTS_PATH, läser artnamn från en CSV-fil,
    och skapar en JavaScript-fil med en datastruktur för alla runs och deras
    respektive arter med namn på flera språk.
    """
    
    # --- NYTT: Steg 1 - Läs in artnamnen från CSV-filen ---
    try:
        df_names = pd.read_csv(SPECIES_NAMES_CSV, sep=';', encoding='utf-8')
        # Skapar en dictionary för snabba uppslag, med latinskt namn som nyckel.
        name_lookup = df_names.set_index('latin_name').to_dict('index')
        print(f"✅ Läste in {len(name_lookup)} artnamn från '{SPECIES_NAMES_CSV}'.")
    except FileNotFoundError:
        print(f"❌ VARNING: '{SPECIES_NAMES_CSV}' hittades inte. Kommer endast använda latinska namn.")
        name_lookup = {}
    except KeyError:
        print(f"❌ VARNING: CSV-filen måste innehålla kolumnen 'latin_name'. Använder endast latinska namn.")
        name_lookup = {}
    except Exception as e:
        print(f"❌ FEL vid inläsning av CSV-fil: {e}")
        name_lookup = {}

    # --- Steg 2 - Skanna rapportmapparna (din befintliga logik) ---
    reports_data = {}
    print(f"\nSkannar huvudmappen: '{BASE_REPORTS_PATH}'...")

    try:
        # Hitta alla undermappar som börjar med 'Trawl' eller 'Gillnet'.
        run_folders = [d for d in os.listdir(BASE_REPORTS_PATH) if os.path.isdir(os.path.join(BASE_REPORTS_PATH, d)) and d.startswith(('Trawl', 'Gillnet'))]

        if not run_folders:
            print(f"❌ VARNING: Hittade inga undermappar som börjar med 'Trawl' eller 'Gillnet' i '{BASE_REPORTS_PATH}'.")
            return

        print(f"Hittade följande mappar: {', '.join(run_folders)}")

        # Gå igenom varje 'run'-mapp.
        for run_name in sorted(run_folders):
            current_path = os.path.join(BASE_REPORTS_PATH, run_name)
            species_list = []
            
            # Gå igenom alla filer i den aktuella 'run'-mappen.
            for filename in os.listdir(current_path):
                if filename.startswith('ProtectBaltic_ModelReport_') and filename.endswith('.html'):
                    start_index = len('ProtectBaltic_ModelReport_')
                    end_index = filename.rfind('.html')
                    file_key = filename[start_index:end_index]
                    
                    # --- ÄNDRAD LOGIK: Skapa flerspråkigt namnobjekt ---
                    latin_name = file_key.replace('_', ' ')
                    
                    # Hämta namnen för denna art från vår uppslagstabell.
                    species_names_from_csv = name_lookup.get(latin_name)

                    if species_names_from_csv:
                        # Om arten finns i CSV:n, använd namnen därifrån.
                        names_obj = {
                            'sv': species_names_from_csv.get('swedish_name', latin_name),
                            'en': species_names_from_csv.get('english_name', latin_name),
                            'la': latin_name
                        }
                    else:
                        # Fallback om arten inte finns i CSV:n.
                        names_obj = {'sv': latin_name, 'en': latin_name, 'la': latin_name}

                    species_list.append({
                        "names": names_obj,    # ÄNDRAD från "name": pretty_name
                        "fileKey": file_key
                    })

            # ÄNDRAD: Sortera artlistan baserat på det latinska namnet.
            species_list.sort(key=lambda x: x['names']['la'])
            
            # Lägg till listan i vår huvudsakliga datastruktur.
            reports_data[run_name] = species_list
            print(f"  - '{run_name}' innehåller {len(species_list)} rapporter.")

        # Formattera datan som en JavaScript-variabel.
        js_content = f"const reportsData = {json.dumps(reports_data, indent=4)};"

        # Skriv till .js-filen.
        with open(OUTPUT_JS_FILE, 'w', encoding='utf-8') as f:
            f.write(js_content)
            
        print(f"\n✅ Klart! Skapade '{OUTPUT_JS_FILE}' med data från {len(reports_data)} mapp(ar).")

    except FileNotFoundError:
        print(f"❌ FEL: Mappen '{BASE_REPORTS_PATH}' hittades inte.")
    except Exception as e:
        print(f"Ett oväntat fel inträffade: {e}")

if __name__ == '__main__':
    generate_reports_data()
