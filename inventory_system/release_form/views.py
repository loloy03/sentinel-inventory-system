from django.shortcuts import render, redirect
from django.contrib import messages
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from .models import ReleasedStock


# Define the scope and credentials for Google Sheets API
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
CREDENTIALS_FILE = "credentials.json" 

# Create your views here.
def release_form(request):
    if request.method == "POST":
        # Get form data
        production_id = request.POST.get("production_id")
        product = request.POST.get("product_released")
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
        stock_entry = ReleasedStock.objects.create(
            production_id=production_id,
            date=date,
            product=product,
            color=color,
            item_code=item_code,
            quantity=quantity,
            pallet_position=pallet_position,
            status=status,
            warehouse_id=warehouse_id
        )

        # Save to Google Sheet
        worksheet = get_google_sheet()
        if worksheet:
            # Append row to the spreadsheet - without item_code, status, and warehouse_id
            worksheet.append_row(
                [
                    production_id,
                    product,
                    color,
                    item_code,
                    quantity,
                    formatted_date,
                    pallet_position,
                    status,
                    warehouse_id
                ]
            )
            messages.success(
                request,
                f"Stock entry release and added to Google Sheet: {quantity} units of {product} in {color}",
            )
        else:
            messages.error(
                request, "Failed to connect to Google Sheet. Data saved locally only."
            )

        return redirect("release_form:release_form")

    return render(request, "release_form/release_form.html")


def get_google_sheet():
    """Connect to Google Sheets API and return the specific spreadsheet"""
    try:
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            CREDENTIALS_FILE, SCOPE
        )
        client = gspread.authorize(credentials)

        # Open the spreadsheet by its URL
        spreadsheet = client.open_by_url(
            "https://docs.google.com/spreadsheets/d/1FkuU_E8BPxrD2lgLjxwmEJ1tMDvIYUfUU3g34eQe7vc/edit?gid=0#gid=0"
        )

        # Select the first worksheet (you can change this if needed)
        worksheet = spreadsheet.get_worksheet(0)
        return worksheet
    except Exception as e:
        print(f"Error connecting to Google Sheets: {e}")
        return None

