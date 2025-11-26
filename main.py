import fitz
from pathlib import Path
from nicegui import ui


ui.button("PDF importieren", on_click=lambda: ordner).props("icon=file_upload")
ui.button("Sortierung starten", on_click=lambda: ausgabe_ordner).props(
    "icon=play_arrow"
)

ui.run()

ordner = Path(r"C:\Users\Keinp\Downloads\Banfen zum sortieren")
ausgabe_ordner = Path(
    r"C:\Users\Keinp\Desktop\Coding\PDF automatisch sortieren nach RV-Nummer"
)

ausgabe_ordner.mkdir(exist_ok=True)


pdf_dateien = list(ordner.glob("*.pdf"))


for datei in pdf_dateien:
    with fitz.open(datei) as doc:
        print(f"Verarbeite Datei: {datei.name} ({doc.page_count} Seiten)")

        for page_num, page in enumerate(doc):
            rect = fitz.Rect(25, 133, 119, 152)
            text = page.get_textbox(rect)

            print(f"Seite {page_num + 1}: RV-Nummer = {text}")

            new_pdf = fitz.open()
            new_pdf.insert_pdf(doc, from_page=page_num, to_page=page_num)

            safe_name = "".join(c for c in text if c.isalnum() or c in ("-", "_"))
            ausgabedatei = ausgabe_ordner / f"{safe_name}_{page_num + 1}.pdf"

            new_pdf.save(ausgabedatei)
            new_pdf.close()


alle_einzeln = sorted(ausgabe_ordner.glob("*.pdf"))

gesamt_pdf = fitz.open()
for datei in alle_einzeln:
    print(f"Füge hinzu: {datei.name}")
    with fitz.open(datei) as pdf:
        gesamt_pdf.insert_pdf(pdf)

gesamt_pdf.save(ausgabe_ordner / "Sortiert.pdf")
gesamt_pdf.close()

print("Fertig: Sortiert.pdf erstellt.")
