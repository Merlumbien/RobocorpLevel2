from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive
import time
# from RPA.PDF import PDF

@task
def bestelle_roboter_von_RobotSpareBin():
    """
    Bestellt einen Roboter von RobotSpareBin Industries Inc.
    Speichert die Bestellbestätigungs HTML Bereich als PDF Datei
    Speichert den Screenshot des bestellten Roboters
    Bindet den Screenshot des Roboters in das PDF ein
    Erstellt ein ZIP Archiv aller Bestellbestätigungen und Bilder
    """
    oeffne_roboter_bestelll_website()
    bestellungen = get_orders()
    order_for_each(bestellungen)
    archive_receipts()


def oeffne_roboter_bestelll_website():
    """Navigiert zur angegebenen URL"""
    # browser.configure(slowmo=200)
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def get_orders():
    """Downloaded die Bestellungen und gibt sie als result aus"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)
    libr = Tables()
    return libr.read_table_from_csv("orders.csv", columns=["Order number","Head","Body","Legs","Address"])

def close_annoying_modal():
    """Presses the 'OK' button"""
    page = browser.page()
    page.click("text=OK")

def order_for_each(bestellungJa):
    """Bestellt für jede Bestellung"""
    for bestellung in bestellungJa:
        # Hier das durchführen was mit jeder Bestellung geschehen muss
        fill_the_form(bestellung)

def fill_the_form(bestellung):
    """Füllt das Formular für eine übergebene Bestellung aus,
    speichert sich das Bild des Roboters und
    schickt die Bestellung auf der Webseite ab."""
    # print(bestellung["Order number"])
    #T die letzten drei Punkte: https://robocorp.com/docs/courses/build-a-robot-python/create-order-process
    head = {"1": "Roll-a-thor", "2": "Peanut crusher", "3": "D.A.V.E", "4": "Andy Roid", "5": "Spanner mate", "6": "Drillbit 2000"}


    close_annoying_modal()
    page = browser.page()
    page.select_option("#head", str(head[bestellung["Head"]]) + " head")
    page.click("text = " + str(head[bestellung["Body"]]) + " body")
    page.fill("input[placeholder='Enter the part number for the legs']", str(bestellung["Legs"]))
    page.fill("#address", str(bestellung["Address"]))
    page.click("#order")

    time.sleep(1)
    while not order_completed():
        page.click("#order")
        time.sleep(1)

    collect_results(bestellung["Order number"])

    store_receipt_as_pdf(bestellung["Order number"])

    page = browser.page()
    page.click("text=Order another robot")

def order_completed():
    """Überprüft, ob die Bestellung abgeschlossen ist"""
    page = browser.page()
    try:
        # Versuchen Sie, das Element mit der Klasse `alert alert-danger` und dem Text `Server Room Flooded Error` zu finden
        error_element = page.locator("//div[@class='alert alert-danger']")
        if error_element.is_visible():
            return False
        return True
    except:
        return True
    
def collect_results(bestellnummer):
    """Take a screenshot of the page"""
    page = browser.page()
    bildElement = page.locator("#robot-preview-image")
    pathJa = "output/" + bestellnummer + ".png"
    bildElement.screenshot(path=pathJa)

def store_receipt_as_pdf(order_number):
    """Exportiere die Daten zu einem PDF File"""
    page = browser.page()
    sales_results_html = page.locator("#receipt").inner_html()

    pdf = PDF()
    pdfName = "output/" + order_number + ".pdf"
    pdf.html_to_pdf(sales_results_html, pdfName)
    imageName = "output/" + order_number + ".png:align=center"
    # print("Imagename ist " + imageName + " und pdfName ist " + pdfName)
    list_of_files = [
        imageName
    ]
    pdf.add_files_to_pdf(list_of_files, pdfName, True)

def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_zip('output', 'output/receipt.zip', include='*.pdf')