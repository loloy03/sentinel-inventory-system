from django.shortcuts import render, redirect
from django.contrib import messages
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from .models import ReceivedStock

# Define the scope and credentials for Google Sheets API
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
CREDENTIALS_FILE = "credentials.json" 


# Create your views here.
def receive_form(request):
    return render(request, "receive_form/receive_form.html")


def get_google_sheet():
    """Connect to Google Sheets API and return the specific spreadsheet"""
    try:
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            CREDENTIALS_FILE, SCOPE
        )
        client = gspread.authorize(credentials)

        # Open the spreadsheet by its URL
        spreadsheet = client.open_by_url(
            "https://docs.google.com/spreadsheets/d/1w_4eJdKW5l5WeSk5F4yAKARFxUhZVbx9j3_ujeS_BZ0/edit?gid=1727869081#gid=1727869081"
        )

        # Select the first worksheet (you can change this if needed)
        worksheet = spreadsheet.get_worksheet(0)
        return worksheet
    except Exception as e:
        print(f"Error connecting to Google Sheets: {e}")
        return None


def receive_form(request):
    if request.method == "POST":
        # Get form data
        production_id = request.POST.get("production_id")
        product = request.POST.get("product_received")
        color = request.POST.get("color")
        quantity = int(request.POST.get("quantity"))
        date = request.POST.get("date")

        # Create item code by combining product and color
        item_code = f"{product}{color}"

        # Format the date as shown in the Google Sheet
        formatted_date = datetime.strptime(date, "%Y-%m-%d").strftime("%m-%d-%Y")

        # Save to database
        stock_entry = ReceivedStock.objects.create(
            production_id=production_id,
            date=date,
            product=product,
            color=color,
            item_code=item_code,
            quantity=quantity,
        )

        # Save to Google Sheet
        worksheet = get_google_sheet()
        if worksheet:
            # Append row to the spreadsheet
            worksheet.append_row(
                [
                    production_id,
                    formatted_date,
                    product,
                    color,
                    item_code,
                    quantity,
                    "RECEIVED",
                ]
            )
            messages.success(
                request,
                f"Stock entry received and added to Google Sheet: {quantity} units of {product} in {color}",
            )
        else:
            messages.error(
                request, "Failed to connect to Google Sheet. Data saved locally only."
            )

        return redirect("receive_form:receive_form")

    return render(request, "receive_form/receive_form.html")
