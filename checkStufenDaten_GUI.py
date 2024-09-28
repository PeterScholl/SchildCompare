import os
import tkinter as tk
import checkStufenDaten_2 as logic
import webbrowser
from tkinter import ttk, messagebox, filedialog


# Define a mapping for special characters
my_char_map = {
    'ć': 'c',
    'ç': 'c',
    'Ç': 'C',
    'é': 'e',
    'è': 'e',
    'ê': 'e',
    'ñ': 'n',
    # Add more mappings as needed
}

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
        self.verglMitLehrer = tk.BooleanVar(value=False)  # Vergleiche ohne Lehrer
        self.verglMitKursBez = tk.BooleanVar(value=False) #Vergleiche mit KursBez
        self.verglMitWochenStd = tk.BooleanVar(value=False) #Vergleiche auch mit Wochenstunden
        self.glFaecherZusammen = tk.BooleanVar(value=True) # Kommt ein Fach mehrfach bei einem Schüler vor
        self.zahlenUntisEntf = tk.BooleanVar(value=True) #Zahlen aus Lehrerkürzeln bei Untis werden entfernt
        self.wenigerAls2Faecher = tk.BooleanVar(value=True) # Schüler mit weniger als zwei Fächern nicht mit LuPO vergl.
        self.sonderzeichenErsetzen = tk.BooleanVar(value=True) #Ersetzt Sonderzeichen aus der Charmap

    def adjust_size(self, new_window):
        # Let Tkinter calculate the required size
        new_window.update_idletasks()
        new_window.geometry("")  # Reset geometry to fit the content

        # Get actual window position
        window_x = new_window.winfo_x()
        window_y = new_window.winfo_y()

        # Resize window to fit content, but keep its position
        #new_size = f"{new_window.winfo_width()}x{new_window.winfo_height()}+{window_x}+{window_y}"
        new_size = f"+{window_x}+{window_y}"
        #print(f"new size: {new_size}")
        new_window.geometry(new_size)
        
    def choose_directory(self, event):
        # Öffnet den Verzeichnisauswahldialog und aktualisiert das Label
        directory = filedialog.askdirectory(initialdir=self.selected_dir.get())
        if directory:
            self.selected_dir.set(directory)
            self.dir_label.config(text=directory)
            if not logic.check_dirs(directory):
                self.show_directory_prompt()
            
    def create_menu(self):
        # Menüleiste erstellen
        menubar = tk.Menu(self)
        
        # Menü "Datei"
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Einstellungen", command=self.open_settings_window)
        file_menu.add_command(label="Info/Hilfe", command=self.open_help_window)
        file_menu.add_separator()
        file_menu.add_command(label="Beenden", command=self.quit)
        menubar.add_cascade(label="Datei", menu=file_menu)
        
        # Menüleiste konfigurieren
        self.config(menu=menubar)
    
    def create_import_status_boxes(self):
        # Frame für Status-Labels
        status_frame = tk.Frame(self)
        status_frame.pack(pady=10)
        
        # Verzeichnisanzeige Label mit Klick-Funktion
        self.selected_dir = tk.StringVar(value=os.getcwd())  # Startet mit dem aktuellen Verzeichnis
        self.dir_label = tk.Label(status_frame, text=self.selected_dir.get(), relief=tk.SUNKEN, width=80, fg="blue", cursor="hand2")
        self.dir_label.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        self.dir_label.bind("<Button-1>", self.choose_directory)  # Klickbare Funktion

        # Status Labels für die drei Importe
        self.schild_label = tk.Label(status_frame, text="Schild-Import: Nicht überprüft", relief=tk.SUNKEN, width=50)
        self.schild_label.grid(row=1, column=0, padx=5, pady=5)
        ToolTip(self.schild_label,"Export Schild: Zunächst Stufe auswäheln (AKTIVE und Externe)\n"+
                "dann in das Menü Datenaustausch, Schild-NRW-Schnittstelle, Export\n"+
                "Alle Haken aus, bis auf Schüler: Leistungsdaten\n"+
                "Rechts: nur aktuellen Abschnitt auswählen -> Export starten")
        
        self.untis_label = tk.Label(status_frame, text="Untis-Import: Nicht überprüft", relief=tk.SUNKEN, width=50)
        self.untis_label.grid(row=2, column=0, padx=5, pady=5)
        ToolTip(self.untis_label,"Export Untis: Menü Datei -> Import/Export -> Deutschland -> NRW-SchildNRW\n"+
                "Reiter Exportieren auswählen - Klasse auswählen - Ordner auswählen - exportieren")
        
        self.lupo_label = tk.Label(status_frame, text="LuPO-Import: Nicht überprüft", relief=tk.SUNKEN, width=50)
        self.lupo_label.grid(row=3, column=0, padx=5, pady=5)
        ToolTip(self.lupo_label,"Export LuPO: Datenaustausch -> SchildNRW -> Exportieren")
    
    def open_help_window(self):
        # Fenster für die Hilfe
        help_window = tk.Toplevel(self)
        help_window.title("Hilfe")
        #help_window.geometry("300x150")
        
        # Info-Label
        info_label = tk.Label(help_window, text="Anleitung\n\n"+
            "Wähle zuerst ein Verzeichnis, in dem die Dateien der verschiedenen\n"+
            "Datenbanken abgelegt werden sollen. Danach werden export-Verzeichnisse\n"+
            "für jedes System angelegt.\n"+
            "Nun können in diese Export-Ordner von jeder Datenquelle die Leistungsdaten\n"+
            "exportiert werden. Dabei soll das UTF-8-Format gewählt werden.\n"+
            "Hilfe erhält man, wenn man mit der Maus über das Status-Feld der\n"+
            "entsprechenden Datenbank fährt.\n"+
            "Wenn alle Export-Dateien generiert worden sind, können noch Einstellungen\n"+
            "im Datei-Menü angepasst werden. Dann kann auf Report geklickt werden.")
        info_label.pack(pady=10)
        
        # Link-Label
        link = tk.Label(help_window, text="Github-Projekt-Website", fg="blue", cursor="hand2")
        link.pack()

        # Funktion zum Öffnen des Links
        link.bind("<Button-1>", lambda e: webbrowser.open_new("https://github.com/PeterScholl/SchildCompare"))

        # Schließen-Button
        close_button = tk.Button(help_window, text="Schließen", command=help_window.destroy)
        close_button.pack(pady=10)
        help_window.after(80, lambda: self.adjust_size(help_window))
    
    def open_settings_window(self):
        # Fenster für Einstellungen
        settings_window = tk.Toplevel(self)
        settings_window.title("Einstellungen")
        #Geometry soll später dem Inhalt angepasst werden
        #settings_window.geometry("200x320")
        
        # Checkbuttons für Einstellungen
        ckButtonAG = tk.Checkbutton(settings_window, text="AGs loeschen", variable=self.loescheAGs)
        ckButtonAG.pack(anchor="w", padx=10, pady=5)
        ToolTip(ckButtonAG,"Bei allen Leistungsdaten werden die Fächer OAG, AG, AGGT gelöscht")
        
        ckButtonLehrer = tk.Checkbutton(settings_window, text="Lehrer prüfen", variable=self.verglMitLehrer)
        ckButtonLehrer.pack(anchor="w", padx=10, pady=5)
        ToolTip(ckButtonLehrer, "Beim Vergleich der Leistungsdaten werden verschiedene Lehrer\n z.B. in Untis oder Schild beachtet")

        ckButtonKursBez = tk.Checkbutton(settings_window, text="Kursbezeichnung prüfen", variable=self.verglMitKursBez)
        ckButtonKursBez.pack(anchor="w", padx=10, pady=5)
        ToolTip(ckButtonLehrer, "Beim Vergleich der Leistungsdaten wird auch die Kursbezeichnung D-GK1 oder D GK1 beachtet\n"+
                "ACHTUNG: LuPO kennt keine Kurse")

        ckButtonWochenStd = tk.Checkbutton(settings_window, text="Wochenstundenzahl prüfen", variable=self.verglMitWochenStd)
        ckButtonWochenStd.pack(anchor="w", padx=10, pady=5)
        ToolTip(ckButtonLehrer, "Beim Vergleich der Leistungsdaten wird auch die Wochenstundenzahl beachtet")

        ckButtonGlFchr = tk.Checkbutton(settings_window, text="Gleiche Fächer zusammenfassen", variable=self.glFaecherZusammen)
        ckButtonGlFchr.pack(anchor="w", padx=10, pady=5)
        ToolTip(ckButtonGlFchr, "Gibt es bei einem Schüler ein Fach mehrfach\n so werden diese zusammengefasst")

        ckButtonZahlenUntis = tk.Checkbutton(settings_window, text="Zahlen aus Lehrerkürzeln bei Untis entfernen", variable=self.zahlenUntisEntf)
        ckButtonZahlenUntis.pack(anchor="w", padx=10, pady=5)
        ToolTip(ckButtonZahlenUntis, "Entfernt die Zahlen aus Lehrerkürzeln, z.B. Extern9, ...")

        ckButtonWenigerAls2Faecher = tk.Checkbutton(settings_window, text="Weniger als 3 Fächer nicht mit LuPO vergl.", variable=self.wenigerAls2Faecher)
        ckButtonWenigerAls2Faecher.pack(anchor="w", padx=10, pady=5)
        ToolTip(ckButtonWenigerAls2Faecher, "Vergleicht Schüler mit weniger als drei Fächern nicht mit LuPO\nExterne Schüler werden dadurch ignoriert")

        ckButtonSonderzeichen = tk.Checkbutton(settings_window, text="Sonderzeichen ersetzen", variable=self.sonderzeichenErsetzen)
        ckButtonSonderzeichen.pack(anchor="w", padx=10, pady=5)
        ToolTip(ckButtonSonderzeichen, "Ersetzt einige Sonderzeichen nach einer festgelegten Tabelle")

        # Schließen Button
        tk.Button(settings_window, text="Schließen", command=settings_window.destroy).pack(pady=10)
        
        # Let Tkinter calculate the required size
        settings_window.after(80, lambda: self.adjust_size(settings_window))
        
        
    def generate_report(self):
        if not logic.check_dirs(self.selected_dir.get()):
                self.show_directory_prompt()
               
        # Simuliert den Import-Status-Check und erstellt den Report
        schild_import_ok, schild_import_result = logic.check_files('schild-export',self.selected_dir.get())
        untis_import_ok, untis_import_result = logic.check_files('untis-export',self.selected_dir.get())
        lupo_import_ok, lupo_import_result = logic.check_files('lupo-export',self.selected_dir.get())
        
        # Import-Status anzeigen
        self.update_status(self.schild_label, schild_import_ok, "Schild", schild_import_result)
        self.update_status(self.untis_label, untis_import_ok, "Untis", untis_import_result)    
        self.update_status(self.lupo_label, lupo_import_ok, "LuPO", lupo_import_result)
        
        # Report als Textdatei speichern und im Fenster anzeigen
        report = f"Schild-Import: {f'{schild_import_result}' if schild_import_ok else f'Missing files: {schild_import_result}'}\n"
        report += f"Untis-Import: {f'{untis_import_result}' if untis_import_ok else f'Missing files: {untis_import_result}'}\n"
        report += f"LuPO-Import: {f'{lupo_import_result}' if lupo_import_ok else f'Missing files: {lupo_import_result}'}\n"
        
        if (schild_import_ok and untis_import_ok and lupo_import_ok):
            #hier können Jetzt die Prüfungen durchgeführt werden
            if (not self.sonderzeichenErsetzen.get()):
                char_map = {}
            else:
                char_map = my_char_map
                
            schild_data = logic.read_csv_file('schild-export', 'SchuelerLeistungsdaten.dat',self.selected_dir.get(),char_map=char_map)
            untis_data = logic.read_csv_file('untis-export', 'SchuelerLeistungsdaten.dat',self.selected_dir.get(),char_map=char_map)
            lupo_data = logic.read_csv_file('lupo-export', 'SchuelerLeistungsdaten.dat',self.selected_dir.get(),char_map=char_map)
            jahr,abschnitt,klasse = logic.get_year_section_class_from_lupo(lupo_data)
            report += f"Jahr: {jahr} - Abschnitt: {abschnitt} - Klasse: {klasse} - aus LuPO-Datei\n"
            len_schild_data_orig = len(schild_data)
            report += f"Schild enthält {len_schild_data_orig} Datensätze\n"
            len_untis_data_orig = len(untis_data)
            report += f"Untis  enthält {len_untis_data_orig} Datensätze\n"
            len_lupo_data_orig = len(lupo_data)
            report += f"LuPO   enthält {len_lupo_data_orig} Datensätze\n"
            #Nur die Daten die zu Jahr, Abschnitt und Klasse passen werden benötigt
            schild_data = logic.filter_data_by_year_section(schild_data,jahr,abschnitt,klasse)
            untis_data = logic.filter_data_by_year_section(untis_data,jahr,abschnitt,klasse)
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
            if (self.wenigerAls2Faecher.get()):
                #Nur Schüler mit mindestens zwei Fächern
                schild_students_forLupo = logic.count_students_minCount(schild_data,3)
                report+=f"Für LuPO werden die Schilddaten auf {len(schild_students_forLupo)} reduziert\n"
            else:
                schild_students_forLupo = schild_students
            
            untis_students = logic.count_students(untis_data)
            lupo_students = logic.count_students(lupo_data)
            report += f"Anzahlen: Schild - {len(schild_students)} SuS, Untis - {len(untis_students)} SuS, LuPO - {len(lupo_students)}\n\n"
            if (len(schild_students_forLupo-lupo_students) > 0):
                report += f"In LuPO fehlen folgende Schüler aus Schild {schild_students_forLupo-lupo_students}\n"
            if (len(lupo_students - schild_students_forLupo) > 0):
                report += f"LuPO hat die folgenden Schüler zu viel {lupo_students-schild_students_forLupo}\n"
            if (len(schild_students-untis_students) > 0):
                report += f"In Untis fehlen folgende Schüler aus Schild {schild_students-untis_students}\n"
            if (len(untis_students - schild_students) > 0):
                report += f"Untis hat die folgenden Schüler zu viel {untis_students-schild_students}\n"
                
                
            #Fachwahlen vergleichen
            columns = ['Jahr', 'Abschnitt','Fach','Kursart']
            if (self.verglMitLehrer.get()):
                columns += ['Fachlehrer']
            if (self.verglMitKursBez.get()):
                columns += ['Kurs']
            if (self.verglMitWochenStd.get()):
                columns += ['Wochenstd.']
            
            report += logic.compare_subject_choices_report(schild_data,untis_data,lupo_data,columns,self.wenigerAls2Faecher.get())
                  
            

            pass
        else:
            report += "Ein Report kann erst generiert werden, wenn alle Daten vorhanden sind\n"
        
        with open('report.txt', 'w',encoding='utf-8') as f:
            f.write(report)
        
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(tk.END, report)
    
    def update_status(self, label, status_ok, name, import_result):
        # Aktualisiert die Anzeige der Import-Status
        if (status_ok):
            label.config(text=f"{name}: OK - {import_result}", bg="lightgreen")
        else:
            label.config(text=f"{name}-Import: Missing Files {import_result}", bg="lightcoral")


    def show_directory_prompt(self):
        dialog_window = tk.Toplevel()  # Neues Fenster, damit es nicht das Hauptfenster beeinflusst
        dialog_window.title("Verzeichnisse anlegen")

        label = tk.Label(dialog_window, text="Die Verzeichnisse für die Exportdateien existieren nicht. Sollen diese nun angelegt werden?")
        label.pack(padx=20, pady=20)

        def on_ok():
            messagebox.showinfo("Verzeichnisse", "Verzeichnisse werden angelegt.")
            logic.check_and_create_dirs(self.selected_dir.get())
            dialog_window.destroy()  # Fenster schließen, wenn "OK" geklickt wird

        def on_cancel():
            messagebox.showinfo("Verzeichnisse", "Aktion abgebrochen.")
            dialog_window.destroy()  # Fenster schließen, wenn "Abbrechen" geklickt wird

        ok_button = tk.Button(dialog_window, text="OK", command=on_ok)
        cancel_button = tk.Button(dialog_window, text="Abbrechen", command=on_cancel)

        ok_button.pack(side="left", padx=10, pady=10)
        cancel_button.pack(side="right", padx=10, pady=10)

        dialog_window.transient()  # Damit es über dem Hauptfenster bleibt
        dialog_window.grab_set()   # Modal machen, damit nur dieses Fenster bedienbar ist
        dialog_window.wait_window()  # Warten, bis das Fenster geschlossen wird

    # Aufruf der Methode, z.B. nach einer bestimmten Aktion
    # show_directory_prompt()


# Anwendung starten
if __name__ == "__main__":
    app = ReportApp()
    app.mainloop()
