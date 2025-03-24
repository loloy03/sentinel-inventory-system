from django.shortcuts import render, redirect
from django.contrib import messages
import json
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
    # Initialize a variable to store success data for the template
    success_data = None

    if request.method == "POST":
        # Get form data
        production_id = request.POST.get("production_id")
        product = request.POST.get("product_received")
        color = request.POST.get("color")
        quantity = int(request.POST.get("quantity"))
        date = request.POST.get("date")
        status = request.POST.get("status")
        pallet_position = request.POST.get("pallet_position")

        # Create item code by combining product and color
        item_code = f"{product}{color}"

        # Create warehouse ID
        warehouse_id = f"{production_id}{pallet_position}"

        # Format the date as shown in the Google Sheet
        formatted_date = datetime.strptime(date, "%Y-%m-%d").strftime("%m/%d/%Y")

        # Save to database
        stock_entry = ReceivedStock.objects.create(
            production_id=production_id,
            date=date,
            product=product,
            color=color,
            item_code=item_code,
            quantity=quantity,
            pallet_position=pallet_position,
            status=status,
            warehouse_id=warehouse_id,
        )

        # Prepare row data for Google Sheets
        row_data = [
            production_id,
            product,
            color,
            item_code,
            quantity,
            formatted_date,
            pallet_position,
            status,
            warehouse_id,
        ]

        # Save to appropriate Google Sheets based on status
        success = save_to_multiple_sheets(status, row_data)

        if success:
            # Store success data for the confirmation display
            success_data = {
                "production_id": production_id,
                "product": product,
                "color": color,
                "quantity": quantity,
                "date": formatted_date,
                "status": status,
                "pallet_position": pallet_position,
                "warehouse_id": warehouse_id,
                "item_code": item_code,
            }

            messages.success(
                request,
                f"Stock entry received and added to Google Sheets: {quantity} units of {product} in {color}",
            )
        else:
            messages.error(
                request, "Failed to connect to Google Sheets. Data saved locally only."
            )

    return render(
        request, "receive_form/receive_form.html", {"success_data": success_data}
    )


def save_to_multiple_sheets(status, row_data):
    """Save data to multiple Google Sheets based on status"""
    try:
        # First sheet based on status
        status_sheet = get_google_sheet(status)
        if not status_sheet:
            return False

        # Append to the status-specific sheet
        status_sheet.append_row(row_data)

        # Also append to the common sheet
        common_sheet_url = "https://docs.google.com/spreadsheets/d/13-dHMhSiirfq6QS4_IBuUiCdnSBjKO8axL4XSP_7M6g/edit?gid=0#gid=0"
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            CREDENTIALS_FILE, SCOPE
        )
        client = gspread.authorize(credentials)
        common_spreadsheet = client.open_by_url(common_sheet_url)
        common_worksheet = common_spreadsheet.get_worksheet(0)

        if common_worksheet:
            common_worksheet.append_row(row_data)

        return True
    except Exception as e:
        print(f"Error saving to Google Sheets: {e}")
        return False


def get_google_sheet(status):
    """Connect to Google Sheets API and return the specific spreadsheet based on status"""
    try:
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            CREDENTIALS_FILE, SCOPE
        )
        client = gspread.authorize(credentials)

        # Determine which spreadsheet to use based on status
        if status == "NEW":
            spreadsheet_url = "https://docs.google.com/spreadsheets/d/1WKcH16KLnrtcbve9kzWB_5R-DiN_Jk6WzxI_TdG61xU/edit?gid=1727869081#gid=1727869081"
        elif status == "REFORMED":
            spreadsheet_url = "https://docs.google.com/spreadsheets/d/1DjGwJt_yfsjH1XWqEt4qfwPq2G79IuxdDvYIhA2wHe4/edit"
        else:
            # Default spreadsheet (original one) for backward compatibility
            spreadsheet_url = "https://docs.google.com/spreadsheets/d/1FkuU_E8BPxrD2lgLjxwmEJ1tMDvIYUfUU3g34eQe7vc/edit?gid=0#gid=0"

        # Open the spreadsheet by its URL
        spreadsheet = client.open_by_url(spreadsheet_url)

        # Select the first worksheet (you can change this if needed)
        worksheet = spreadsheet.get_worksheet(0)
        return worksheet
    except Exception as e:
        print(f"Error connecting to Google Sheets: {e}")
        return None


def warehouse_outside(request):
    """Render the warehouse layout page"""
    return render(request, "receive_form/warehouse_layouts/warehouse_outside.html")


def warehouse_area(request):
    """Render the warehouse layout page with database records"""
    # Get all received stock records
    pallet_records = ReceivedStock.objects.all()

    # Convert to a format that can be used in JavaScript
    # Aggregate quantities for the same pallet position
    pallet_data = {}

    for record in pallet_records:
        pallet_code = record.pallet_position

        if pallet_code in pallet_data:
            # Add to existing quantity for this pallet position
            pallet_data[pallet_code]["quantity"] += record.quantity

            # Update the date to the most recent one
            record_date = record.date.strftime("%m/%d/%Y")
            if record_date > pallet_data[pallet_code]["date"]:
                pallet_data[pallet_code]["date"] = record_date
        else:
            # Create new entry for this pallet position
            pallet_data[pallet_code] = {
                "production_id": record.production_id,
                "product": record.product,
                "color": record.color,
                "quantity": record.quantity,
                "date": record.date.strftime("%m/%d/%Y"),
                "status": record.status,
            }

    return render(
        request,
        "receive_form/warehouse_layouts/warehouse_area.html",
        {"pallet_data_json": json.dumps(pallet_data)},
    )
