import os
import csv
from datetime import datetime
from collections import defaultdict

# Verzeichnisse
directories = {
    'schild-export': ['Schueler_IDs.dat', 'SchuelerLeistungsdaten.dat'],
    'untis-export': ['SchuelerLeistungsdaten.dat'],
    'lupo-export': ['SchuelerLeistungsdaten.dat']
}
explanation = {
    'schild-export': "\nExportanleitung Schild:\nWähle in Schild den Jahrgang aus (z.B. Q2 - inklusive Externer) gehe auf Datenaustausch ->"+
            "Export für Lupo-> Initial-Export und wähle bei Wie sollen die Daten exportiert werden - Schnittstellendatei\n",
    'untis-export': "\nExportanleitung Untis:\nExport-Deutschland-SchildNRW-(Klasse auswählen)\n",
    'lupo-export': "\nExportanleitung für LuPO:\nDatenaustausch-Schnittstelle SchildNRW-Export - Schueler und Laufbahndaten, dann das "+
    "richtige Halbjahr wählen und den richtigen Abschnitt - UTF8-Datei - keine Nachfolgehalbjahre\n"
}

# Verzeichnisprüfung und -erstellung
def check_and_create_dirs():
    for directory in directories.keys():
        if not os.path.exists(directory):
            print(f"Verzeichnis '{directory}' existiert nicht. Erstelle es.")
            os.makedirs(directory)
        else:
            print(f"Verzeichnis '{directory}' existiert bereits.")

# Datei-Überprüfung und Änderungsdatum ermitteln
def check_files():
    for directory, files in directories.items():
        print(f"\nPrüfe Verzeichnis: {directory}")
        missing_files = []
        for file in files:
            file_path = os.path.join(directory, file)
            if os.path.exists(file_path):
                # Änderungsdatum ermitteln
                mod_time = os.path.getmtime(file_path)
                print(f"Datei '{file}' gefunden. Änderungsdatum: {datetime.fromtimestamp(mod_time)}")
            else:
                print(f"Datei '{file}' fehlt.")
                missing_files.append(file)
        
        # Benutzerabfrage bei fehlenden Dateien
        if missing_files:
            print(explanation.get(directory))
            input(f"Bitte exportiere die fehlenden Dateien: {', '.join(missing_files)} in {directory}. Drücke Enter, um die Prüfung zu wiederholen.")
            return False
    return True

# CSV-Datei einlesen
def read_csv_file(directory, file_name):
    file_path = os.path.join(directory, file_name)
    rows = []
    if os.path.exists(file_path):
        with open(file_path, mode='r', newline='', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file, delimiter='|')
            for row in reader:
                rows.append(row)
    else:
        print(f"Datei '{file_name}' im Verzeichnis '{directory}' nicht gefunden.")
    return rows

# Schüler zählen (eindeutige Schüler anhand von Nachname, Vorname, Geburtsdatum)
def count_students(data):
    unique_students = set()
    for row in data:
        #print(row.keys())
        student_key = (row['Nachname'], row['Vorname'], row['Geburtsdatum'])
        unique_students.add(student_key)
    return unique_students

# Fächer zusammenführen und Stundenzahlen addieren, mit Ausgabe bei doppelten Fächern und Kursart-Überprüfung
def merge_subjects_with_same_name(data):
    merged_data = defaultdict(lambda: {})
    
    for row in data:
        student_key = (row['Nachname'], row['Vorname'], row['Geburtsdatum'])
        subject_key = (row['Fach'], row['Jahr'], row['Abschnitt'])
        
        # Überprüfen, ob das Fach bereits für diesen Schüler existiert
        if subject_key in merged_data[student_key]:
            # Ausgabe für doppeltes Fach
            print(f"Doppeltes Fach für Schüler {row['Nachname']} {row['Vorname']} ({row['Geburtsdatum']}): {row['Fach']}")
            
            # Kursart-Überprüfung
            existing_course_type = merged_data[student_key][subject_key].get('Kursart', '')
            if existing_course_type and existing_course_type != row['Kursart']:
                print(f"Unterschiedliche Kursart für {row['Fach']}: Vorher '{existing_course_type}', jetzt '{row['Kursart']}'")
            
            # Stundenzahlen addieren, wenn sie vorhanden sind
            merged_data[student_key][subject_key]['Wochenstd.'] += float(row['Wochenstd.'])
            
            # Zusatzkraft-Wochenstunden nur addieren, wenn der Wert nicht leer ist
            if row['Wochenstd. ZK']:
                merged_data[student_key][subject_key]['Wochenstd. ZK'] += float(row['Wochenstd. ZK'])
        else:
            # Andernfalls Fach hinzufügen, wenn es neu ist
            merged_data[student_key][subject_key] = {
                'Fach': row['Fach'],
                'Jahr': row['Jahr'],
                'Abschnitt': row['Abschnitt'],
                'Fachlehrer': row['Fachlehrer'],
                'Kurs': row['Kurs'],
                'Wochenstd.': float(row['Wochenstd.']),
                'Zusatzkraft': row['Zusatzkraft'],
                'Wochenstd. ZK': float(row['Wochenstd. ZK']) if row['Wochenstd. ZK'] else 0,
                'Kursart': row['Kursart']  # Kursart speichern
            }
    
    # Ausgabe: Liste von zusammengeführten Fächern pro Schüler
    result = []
    for student, subjects in merged_data.items():
        for subject_key, subject_data in subjects.items():
            # Debugging: Struktur von subject_data ausgeben
            #print(f"subject_data: {subject_data}")  # Nur für Debugging
            
            combined_row = {
                'Nachname': student[0],
                'Vorname': student[1],
                'Geburtsdatum': student[2],
                'Fach': subject_data['Fach'],  # Fehlerhafte Zeile zuvor, nun behoben
                'Fachlehrer': subject_data['Fachlehrer'],
                'Kurs': subject_data['Kurs'],
                'Jahr': subject_data['Jahr'],
                'Abschnitt': subject_data['Abschnitt'],
                'Wochenstd.': subject_data['Wochenstd.'],
                'Zusatzkraft': subject_data['Zusatzkraft'],
                'Wochenstd. ZK': subject_data['Wochenstd. ZK'],
                'Kursart': subject_data['Kursart']
            }
            result.append(combined_row)
    
    return result

# Schüler vergleichen, ob sie in allen drei Datensätzen vorhanden sind
def compare_students(schild_data, untis_data, lupo_data):
    schild_students = count_students(schild_data)
    untis_students = count_students(untis_data)
    lupo_students = count_students(lupo_data)
    
    all_students = schild_students.union(untis_students, lupo_students)
    
    missing_in_schild = all_students - schild_students
    missing_in_untis = all_students - untis_students
    missing_in_lupo = all_students - lupo_students
    
    print("\n=== Schüler-Vergleich ===")
    print(f"Anzahlen: Schild - {len(schild_students)} SuS, Untis - {len(untis_students)} SuS, LuPO - {len(lupo_students)}")
    if missing_in_schild:
        print(f"Fehlende Schüler in 'schild-export': {missing_in_schild}")
    if missing_in_untis:
        print(f"Fehlende Schüler in 'untis-export': {missing_in_untis}")
    if missing_in_lupo:
        print(f"Fehlende Schüler in 'lupo-export': {missing_in_lupo}")
    
    return all_students

# Fachwahlen für Schüler vergleichen und Unterschiede anzeigen
def compare_subject_choices(schild_data, untis_data, lupo_data):
    def create_subject_key(row, ignore_teacher_and_course=False):
        # Wenn ignore_teacher_and_course True ist, werden 'Fachlehrer' und 'Kurs' nicht verwendet (für LuPO)
        if ignore_teacher_and_course:
            return (row['Jahr'], row['Abschnitt'], row['Fach'], row['Kursart'])
        else:
            return (row['Jahr'], row['Abschnitt'], row['Fach'], row['Fachlehrer'], row['Kursart'], row['Kurs'])
    
    schild_dict = defaultdict(list)
    schild_dict_reduced = defaultdict(list)
    untis_dict = defaultdict(list)
    untis_dict_reduced = defaultdict(list)
    lupo_dict = defaultdict(list)
    
    # Daten in Dictionaries nach Schülern gruppieren
    for row in schild_data:
        student_key = (row['Nachname'], row['Vorname'], row['Geburtsdatum'])
        schild_dict[student_key].append(create_subject_key(row))
        # Für den Vergleich mit LuPO wird eine Liste ohne Fachlehrer und Kurs angelegt
        schild_dict_reduced[student_key].append(create_subject_key(row, ignore_teacher_and_course=True))
    
    for row in untis_data:
        student_key = (row['Nachname'], row['Vorname'], row['Geburtsdatum'])
        untis_dict[student_key].append(create_subject_key(row))
        # Für den Vergleich mit LuPO wird eine Liste ohne Fachlehrer und Kurs angelegt
        untis_dict_reduced[student_key].append(create_subject_key(row, ignore_teacher_and_course=True))
    
    for row in lupo_data:
        student_key = (row['Nachname'], row['Vorname'], row['Geburtsdatum'])
        # Für LuPO wird der Vergleich ohne Fachlehrer und Kurs durchgeführt
        lupo_dict[student_key].append(create_subject_key(row, ignore_teacher_and_course=True))
    
    # Vergleich der Fachwahlen
    print("\n=== Fachwahl-Vergleich ===")
    for student in schild_dict:
        schild_subjects = set(schild_dict[student])
        schild_subjects_red = set(schild_dict_reduced[student])
        untis_subjects = set(untis_dict.get(student, []))
        untis_subjects_red = set(untis_dict_reduced.get(student, []))
        lupo_subjects = set(lupo_dict.get(student, []))
        
        # Vergleiche Schild- und Untis-Daten
        if schild_subjects != untis_subjects:
            print(f"\nUnterschiedliche Fachwahlen für Schüler {student} zwischen 'schild-export' und 'untis-export':")
            only_in_schild = schild_subjects - untis_subjects
            if only_in_schild:
                print(f"Nur in 'schild-export': {only_in_schild}")
            only_in_untis = untis_subjects - schild_subjects
            if only_in_untis:
                print(f"Nur in 'untis-export': {only_in_untis}")        
        
        
        # Vergleiche Schild- und Lupo-Daten (ohne Fachlehrer und Kurs)
        if schild_subjects_red != lupo_subjects:
            print(f"\nUnterschiedliche Fachwahlen für Schüler {student} zwischen 'schild-export' und 'lupo-export':")
            only_in_schild = schild_subjects_red - lupo_subjects
            if only_in_schild:
                print(f"Nur in 'schild-export': {only_in_schild}")
            only_in_lupo = lupo_subjects - schild_subjects_red
            if only_in_lupo:
                print(f"Nur in 'lupo-export': {only_in_lupo}")

# Hauptfunktion
def main():
    check_and_create_dirs()

    while not check_files():
        print("Prüfung wird wiederholt...")

    # Daten einlesen
    schild_data = read_csv_file('schild-export', 'SchuelerLeistungsdaten.dat')
    untis_data = read_csv_file('untis-export', 'SchuelerLeistungsdaten.dat')
    lupo_data = read_csv_file('lupo-export', 'SchuelerLeistungsdaten.dat')
    
    # 0. Untis Fächer zusammenführen - entsprechende Meldungen erzeugen
    print("\n=== Prüfe doppelte Fächer in Untis-Export ===")
    untis_data = merge_subjects_with_same_name(untis_data)
    
    # 1. Schüler-Vergleich
    compare_students(schild_data, untis_data, lupo_data)
    
    # 2. Fachwahl-Vergleich
    compare_subject_choices(schild_data, untis_data, lupo_data)

    

if __name__ == "__main__":
    main()

