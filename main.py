import fitz
from pathlib import Path
from nicegui import ui


ordner = Path(r"C:\Users\Keinp\Downloads\Banfen zum sortieren")
ausgabe_ordner = Path(
    r"C:\Users\Keinp\Desktop\Coding\PDF automatisch sortieren nach RV-Nummer"
)


ausgabe_ordner.mkdir(exist_ok=True)

pdf_dateien = []


async def handle_upload(e):
    # 1. Inhalt asynchron lesen (wichtig!)
    datei_inhalt = await e.file.read()

    # 2. Name sicher holen
    # Wir schauen NUR in e.file. Wenn dort kein 'filename' ist, nehmen wir den String "unbekannt.pdf".
    # Wir fassen e.name gar nicht mehr an.
    dateiname = getattr(e.file, "filename", "unbekannt.pdf")

    # 3. Speichern
    pdf_dateien.append({"name": dateiname, "content": datei_inhalt})

    ui.notify(f"{dateiname} wurde hochgeladen. ({len(pdf_dateien)} Dateien insgesamt)")


ui.upload(on_upload=handle_upload).classes("max-w-full")

ui.button(
    "Sortierung starten",
    on_click=lambda: (start_sorter(), ui.notify("Sortierung gestartet")),
).props("icon=play_arrow")


def start_sorter():
    if not pdf_dateien:
        ui.notify("Keine Dateien hochgeladen.", type="warning")
        return

    # Sortieren
    pdf_dateien.sort(key=lambda x: x["name"].lower())

    ui.notify("Dateien werden verarbeitet...", type="info")

    for datei in pdf_dateien:
        # Hier wird jetzt echter Inhalt übergeben, keine Coroutine mehr
        with fitz.open("pdf", datei["content"]) as doc:
            print(f"Verarbeite Datei: {datei['name']} ({doc.page_count} Seiten)")

            for page_num, page in enumerate(doc):
                rect = fitz.Rect(25, 133, 119, 152)
                text = page.get_textbox(rect)

                # Bereinigen des Textes für Dateinamen
                safe_name = "".join(
                    c for c in text if c.isalnum() or c in ("-", "_")
                ).strip()
                if not safe_name:
                    safe_name = "Unbekannt"

                print(f"  -> Seite {page_num + 1}: RV-Nummer = {safe_name}")

                # --- WICHTIG: Das hier muss EINGERÜCKT sein ---
                # Damit es für JEDE Seite passiert, nicht nur für die letzte
                new_pdf = fitz.open()
                new_pdf.insert_pdf(doc, from_page=page_num, to_page=page_num)

                ausgabedatei = ausgabe_ordner / f"{safe_name}_{page_num + 1}.pdf"

                # Datei speichern
                new_pdf.save(ausgabedatei)
                new_pdf.close()
                # ---------------------------------------------

    # Zusammenfügen (Merge) am Ende
    alle_einzeln = sorted(ausgabe_ordner.glob("*.pdf"))
    if not alle_einzeln:
        ui.notify("Keine Seiten extrahiert.", type="warning")
        return

    gesamt_pdf = fitz.open()
    for datei_pfad in alle_einzeln:
        # Skip die Sortiert.pdf selbst, falls sie schon existiert
        if datei_pfad.name == "Sortiert.pdf":
            continue

        try:
            with fitz.open(datei_pfad) as pdf:
                gesamt_pdf.insert_pdf(pdf)
        except Exception as err:
            print(f"Fehler beim Mergen von {datei_pfad}: {err}")

    gesamt_pdf.save(ausgabe_ordner / "Sortiert.pdf")
    gesamt_pdf.close()

    ui.notify("Fertig! Datei 'Sortiert.pdf' erstellt.", type="positive")


ui.run()
