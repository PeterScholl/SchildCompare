import tkinter as tk
import checkStufenDaten_2 as logic
from tkinter import ttk, messagebox

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        widget.bind("<Enter>", self.show_tooltip)
        widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        # Tooltip Fenster erstellen
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)  # Kein Fensterrahmen
        self.tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
        label = tk.Label(self.tooltip, text=self.text, background="lightgrey", relief="solid", borderwidth=1)
        label.pack()

    def hide_tooltip(self, event):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None
            
class ReportApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Hauptfenster konfigurieren
        self.title("Schild-LuPO-Untis-Abgleich")
        self.geometry("800x600")
        
        # Menüleiste
        self.create_menu()
        
        # Inhalt: Infoboxen für Importe
        self.create_import_status_boxes()
        
        # Textbox für den Report
        self.report_text = tk.Text(self, height=10, width=50)
        self.report_text.pack(fill='both', expand=True, padx=10, pady=10)  # Rand von 10 Pixeln
        #self.report_text.pack(pady=10)
        
        # Start-Button
        start_button = tk.Button(self, text="Report generieren", command=self.generate_report)
        start_button.pack(pady=10)
        
        # Einstellungen speichern
        self.loescheAGs = tk.BooleanVar(value=True) #AGs sollen geloescht werden
        self.verglOhneLehrer = tk.BooleanVar(value=True)  # Vergleiche ohne Lehrer
        self.glFaecherZusammen = tk.BooleanVar(value=True) # Kommt ein Fach mehrfach bei einem Schüler vor
        self.zahlenUntisEntf = tk.BooleanVar(value=True) #Zahlen aus Lehrerkürzeln bei Untis werden entfernt
    
    def create_menu(self):
        # Menüleiste erstellen
        menubar = tk.Menu(self)
        
        # Menü "Datei"
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Einstellungen", command=self.open_settings_window)
        file_menu.add_separator()
        file_menu.add_command(label="Beenden", command=self.quit)
        menubar.add_cascade(label="Datei", menu=file_menu)
        
        # Menüleiste konfigurieren
        self.config(menu=menubar)
    
    def create_import_status_boxes(self):
        # Frame für Status-Labels
        status_frame = tk.Frame(self)
        status_frame.pack(pady=10)
        
        # Status Labels für die drei Importe
        self.schild_label = tk.Label(status_frame, text="Schild-Import: Nicht überprüft", relief=tk.SUNKEN, width=30)
        self.schild_label.grid(row=0, column=0, padx=5, pady=5)
        ToolTip(self.schild_label,"TODO Anleitung Schild Export")
        
        self.untis_label = tk.Label(status_frame, text="Untis-Import: Nicht überprüft", relief=tk.SUNKEN, width=30)
        self.untis_label.grid(row=1, column=0, padx=5, pady=5)
        ToolTip(self.untis_label,"TODO Anleitung Untis Export")
        
        self.lupo_label = tk.Label(status_frame, text="LuPO-Import: Nicht überprüft", relief=tk.SUNKEN, width=30)
        self.lupo_label.grid(row=2, column=0, padx=5, pady=5)
        ToolTip(self.lupo_label,"TODO Anleitung LuPO Export")
    
    def open_settings_window(self):
        # Fenster für Einstellungen
        settings_window = tk.Toplevel(self)
        settings_window.title("Einstellungen")
        settings_window.geometry("400x200")
        
        # Checkbuttons für Einstellungen
        ckButtonAG = tk.Checkbutton(settings_window, text="AGs loeschen", variable=self.loescheAGs)
        ckButtonAG.pack(anchor="w", padx=10, pady=5)
        ToolTip(ckButtonAG,"Bei allen Leistungsdaten werden die Fächer OAG, AG, AGGT gelöscht")
        
        ckButtonLehrer = tk.Checkbutton(settings_window, text="Lehrer nicht prüfen", variable=self.verglOhneLehrer)
        ckButtonLehrer.pack(anchor="w", padx=10, pady=5)
        ToolTip(ckButtonLehrer, "Beim Vergleich der Leistungsdaten werden verschiedene Lehrer\n z.B. in Untis oder Schild ignoriert")
        
        ckButtonGlFchr = tk.Checkbutton(settings_window, text="Gleiche Fächer zusammenfassen", variable=self.glFaecherZusammen)
        ckButtonGlFchr.pack(anchor="w", padx=10, pady=5)
        ToolTip(ckButtonGlFchr, "Gibt es bei einem Schüler ein Fach mehrfach\n so werden diese zusammengefasst")

        ckButtonZahlenUntis = tk.Checkbutton(settings_window, text="Zahlen aus Lehrerkürzeln bei Untis entfernen", variable=self.zahlenUntisEntf)
        ckButtonZahlenUntis.pack(anchor="w", padx=10, pady=5)
        ToolTip(ckButtonZahlenUntis, "Entfernt die Zahlen aus Lehrerkürzeln, z.B. Extern9, ...")

        # Schließen Button
        tk.Button(settings_window, text="Schließen", command=settings_window.destroy).pack(pady=10)
    
    def generate_report(self):
        logic.check_and_create_dirs()
        # Simuliert den Import-Status-Check und erstellt den Report
        schild_import_ok, schild_import_result = logic.check_files('schild-export')
        untis_import_ok, untis_import_result = logic.check_files('untis-export')
        lupo_import_ok, lupo_import_result = logic.check_files('lupo-export')
        
        # Import-Status anzeigen
        self.update_status(self.schild_label, schild_import_ok, "Schild", schild_import_result)
        self.update_status(self.untis_label, untis_import_ok, "Untis", untis_import_result)    
        self.update_status(self.lupo_label, lupo_import_ok, "LuPO", lupo_import_result)
        
        # Report als Textdatei speichern und im Fenster anzeigen
        report = f"Schild-Import: {'OK' if schild_import_ok else f'Missing files: {schild_import_result}'}\n"
        report += f"Untis-Import: {'OK' if untis_import_ok else 'Fehler'}\n"
        report += f"LuPO-Import: {'OK' if lupo_import_ok else 'Fehler'}\n"
        
        if (schild_import_ok and untis_import_ok and lupo_import_ok):
            #hier können Jetzt die Prüfungen durchgeführt werden
            schild_data = logic.read_csv_file('schild-export', 'SchuelerLeistungsdaten.dat')
            untis_data = logic.read_csv_file('untis-export', 'SchuelerLeistungsdaten.dat')
            lupo_data = logic.read_csv_file('lupo-export', 'SchuelerLeistungsdaten.dat')
            jahr,abschnitt,klasse = logic.get_year_section_class_from_lupo(lupo_data)
            report += f"Jahr: {jahr} - Abschnitt: {abschnitt} - Klasse: {klasse} - aus LuPO-Datei\n"
            len_schild_data_orig = len(schild_data)
            report += f"Schild enthält {len_schild_data_orig} Datensätze\n"
            len_untis_data_orig = len(untis_data)
            report += f"Untis  enthält {len_untis_data_orig} Datensätze\n"
            len_lupo_data_orig = len(lupo_data)
            report += f"LuPO   enthält {len_lupo_data_orig} Datensätze\n"
            #Nur die Daten die zu Jahr, Abschnitt und Klasse passen werden benötigt
            schild_data = logic.filter_data_by_year_section_class(schild_data,jahr,abschnitt,klasse)
            untis_data = logic.filter_data_by_year_section_class(untis_data,jahr,abschnitt,klasse)
            if (len(schild_data) < len_schild_data_orig or len(untis_data) < len_untis_data_orig):
                report += "Erhalte nur die Datensätze zu obigem Abschnitt aus LuPO\n"
                report += f"Schild enthält jetzt {len(schild_data)} Datensätze\n"
                report += f"Untis  enthält jetzt {len(untis_data)} Datensätze\n"
            
            # AGs aus Schild entfernen
            if (self.loescheAGs.get()):
                len_alt = len(schild_data)
                schild_data, tempreport = logic.remove_subjects_from_data(schild_data, ['AG','AGGT','OAG'])
                report += tempreport
                if (len(schild_data)<len_alt):
                    report += f"\n Es wurden {len_alt-len(schild_data)} Eintraege in Schild entfernt\n"
                    
                
            
            # Zahlen aus den Lehrerkürzen entfernen falls gewünscht
            if (self.zahlenUntisEntf.get()):
                report += "\nZahlen aus den Lehrerkürzeln bei Untis werden entfernt\n"
                untis_data = logic.clean_teacher_codes(untis_data)
                
            if (self.glFaecherZusammen.get()):
                # 0. Untis Fächer zusammenführen - entsprechende Meldungen erzeugen
                report += "\n=== Prüfe doppelte Fächer in Untis-Export ==="
                len_alt = len(untis_data)
                untis_data = logic.merge_subjects_with_same_name(untis_data)
                report += f"\n Es wurden {len_alt-len(untis_data)} Eintraege entfernt\n"
                
            #Schüler vergleichen
            report += "\n=== Schüler vergleichen ===\n"
            schild_students = logic.count_students(schild_data)
            untis_students = logic.count_students(untis_data)
            lupo_students = logic.count_students(lupo_data)
            report += f"Anzahlen: Schild - {len(schild_students)} SuS, Untis - {len(untis_students)} SuS, LuPO - {len(lupo_students)}\n\n"
            if (len(schild_students-lupo_students) > 0):
                report += f"In LuPO fehlen folgende Schüler aus Schild {schild_students-lupo_students}\n"
            if (len(lupo_students - schild_students) > 0):
                report += f"LuPO hat die folgenden Schüler zu viel {lupo_students-schild_students}\n"
            if (len(schild_students-untis_students) > 0):
                report += f"In Untis fehlen folgende Schüler aus Schild {schild_students-untis_students}\n"
            if (len(untis_students - schild_students) > 0):
                report += f"Untis hat die folgenden Schüler zu viel {untis_students-schild_students}\n"
                
                
            #Fachwahlen vergleichen
            if (self.verglOhneLehrer.get()):
                columns = ['Jahr', 'Abschnitt','Fach','Kursart']
            else:
                columns = ['Jahr', 'Abschnitt','Fach','Kursart','Fachlehrer','Kurs']
            report += logic.compare_subject_choices_report(schild_data,untis_data,lupo_data,columns)
                  
            

            pass
        else:
            report += "Ein Report kann erst generiert werden, wenn alle Daten vorhanden sind\n"
        
        with open('report.txt', 'w') as f:
            f.write(report)
        
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(tk.END, report)
    
    def update_status(self, label, status_ok, name, import_result):
        # Aktualisiert die Anzeige der Import-Status
        if (status_ok):
            label.config(text=f"{name}: OK - {import_result}", bg="lightgreen")
        else:
            label.config(text="{name}-Import: Missing Files", bg="lightcoral")

# Anwendung starten
if __name__ == "__main__":
    app = ReportApp()
    app.mainloop()
