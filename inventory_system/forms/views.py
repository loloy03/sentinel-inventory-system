from django.shortcuts import render, redirect
from django.contrib import messages
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from .models import FromsStock
from django.db.models import Sum
from django.contrib.auth.decorators import login_required

# Define the scope and credentials for Google Sheets API
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
CREDENTIALS_FILE = "credentials.json"


@login_required
def dashboard(request):
    """Render the dashboard page"""
    return render(request, "dashboard/dashboard.html")


# Create your views here.
def receive_form(request):
    # Initialize a variable to store success data for the template
    success_data = None

    if request.method == "POST":
        # Get form data
        production_code = request.POST.get("production_code")
        product = request.POST.get("product_received")
        color = request.POST.get("color")
        quantity = int(request.POST.get("quantity"))
        date = request.POST.get("date")
        status = request.POST.get("status")
        pallet_position = request.POST.get("pallet_position")

        # Create item code by combining product and color
        item_code = f"{product}{color}"

        # Create warehouse ID
        warehouse_id = f"{production_code}{pallet_position}"

        # Format the date as shown in the Google Sheet
        formatted_date = datetime.strptime(date, "%Y-%m-%d").strftime("%m/%d/%Y")

        # Save to database
        stock_entry = FromsStock.objects.create(
            production_code=production_code,
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
            production_code,
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
                "production_code": production_code,
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


def release_form(request):
    # Initialize a variable to store success data for the template
    success_data = None

    if request.method == "POST":
        # Get form data
        production_code = request.POST.get("production_code")
        product = request.POST.get("product_released")
        color = request.POST.get("color")
        quantity = int(request.POST.get("quantity"))
        date = request.POST.get("date")
        status = request.POST.get("status")
        pallet_position = request.POST.get("pallet_position")

        # Create item code by combining product and color
        item_code = f"{product}{color}"

        # Create warehouse ID
        warehouse_id = f"{production_code}{pallet_position}"

        # Format the date as shown in the Google Sheet
        formatted_date = datetime.strptime(date, "%Y-%m-%d").strftime("%m/%d/%Y")

        try:
            # Find the exact record with the warehouse_id
            stock_record = FromsStock.objects.get(
                warehouse_id=warehouse_id, product=product, color=color
            )

            # Check if there's enough quantity to release
            if stock_record.quantity < quantity:
                messages.error(
                    request,
                    f"Error: Insufficient stock. Available quantity is {stock_record.quantity}",
                )
                return render(
                    request, "release_form/release_form.html", {"success_data": None}
                )

            # Decrease the quantity
            stock_record.quantity -= quantity
            stock_record.save()

        except FromsStock.DoesNotExist:
            # Handle case where no matching record exists
            messages.error(
                request, "Error: No matching stock record found for the given details"
            )
            return render(
                request, "release_form/release_form.html", {"success_data": None}
            )

        # Prepare row data for Google Sheets (still track the release)
        row_data = [
            production_code,
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
                "production_code": production_code,
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
                f"Stock release recorded and updated in Google Sheet: {quantity} units of {product} in {color} released",
            )
        else:
            messages.error(
                request, "Failed to connect to Google Sheet. Data saved locally only."
            )

    return render(
        request, "release_form/release_form.html", {"success_data": success_data}
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
        if status == "NEW" or status == "REFORMED":
            common_sheet_url = "https://docs.google.com/spreadsheets/d/13-dHMhSiirfq6QS4_IBuUiCdnSBjKO8axL4XSP_7M6g/edit?gid=0#gid=0"
        else:
            common_sheet_url = "https://docs.google.com/spreadsheets/d/1M9lsaDLGe1rMOT_0BKLR4Mlp9GgeHLuhiPnCJnZbraQ/edit?gid=1849844819#gid=1849844819"
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
            spreadsheet_url = "https://docs.google.com/spreadsheets/d/1DjGwJt_yfsjH1XWqEt4qfwPq2G79IuxdDvYIhA2wHe4/edit?gid=1247771229#gid=1247771229"
        elif status == "DELIVERY":
            spreadsheet_url = "https://docs.google.com/spreadsheets/d/1Hq9xlDb0_NCrmeDofoQHmrmxrcY5kgwt30f_xJdzAvk/edit?gid=414283636#gid=414283636"
        elif status == "OTHER PROCESSES":
            spreadsheet_url = "https://docs.google.com/spreadsheets/d/1eBcGsl2nLTYFGgHIBjemHsTkKFtG_b_iYFh1DYcW42M/edit?gid=575783866#gid=575783866"
        elif status == "REJECT":
            spreadsheet_url = "https://docs.google.com/spreadsheets/d/1zOFoz5f09H8ocLyDqprNP1zZWJX9YwuVhBl9l7HAdvE/edit?gid=265773487#gid=265773487"
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
    """Render the warehouse layout page with database records"""
    # Get all received stock records
    pallet_records = FromsStock.objects.all()

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
                "production_code": record.production_code,
                "product": record.product,
                "color": record.color,
                "quantity": record.quantity,
                "date": record.date.strftime("%m/%d/%Y"),
                "status": record.status,
            }

    return render(
        request,
        "warehouse_layouts/warehouse_outside.html",
        {"pallet_data_json": json.dumps(pallet_data)},
    )


def warehouse_area(request):
    """Render the warehouse layout page with database records"""
    # Get all received stock records
    pallet_records = FromsStock.objects.all()

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
                "production_code": record.production_code,
                "product": record.product,
                "color": record.color,
                "quantity": record.quantity,
                "date": record.date.strftime("%m/%d/%Y"),
                "status": record.status,
            }

    return render(
        request,
        "warehouse_layouts/warehouse_area.html",
        {"pallet_data_json": json.dumps(pallet_data)},
    )


def search_key(request):
    search_results = None
    total_quantity = 0  # <-- Initialize total quantity
    product_searched = request.POST.get("search_product", None)
    color_searched = request.POST.get("search_color", None)

    if (
        request.method == "POST" and "search_product" in request.POST
    ):  # Check if product form was submitted
        product = request.POST.get("search_product")
        color = request.POST.get("search_color")

        # Query the database for matching records where quantity > 0
        pallet_records = FromsStock.objects.filter(
            product=product, color=color, quantity__gt=0
        )

        # --- Calculate Total Quantity ---
        # Use aggregate to sum the quantity directly from the database query
        total_aggregate = pallet_records.aggregate(total=Sum("quantity"))
        total_quantity = (
            total_aggregate["total"] if total_aggregate["total"] is not None else 0
        )
        # --------------------------------

        # Aggregate quantities for the same pallet position (existing logic)
        pallet_data = {}
        for record in pallet_records:  # Iterate over the already filtered records
            pallet_code = record.pallet_position
            pallet_data[pallet_code] = pallet_data.get(pallet_code, 0) + record.quantity

        # Convert to list of tuples for easier rendering
        search_results = list(pallet_data.items())

    context = {
        "search_results": search_results,
        "product_searched": product_searched,
        "color_searched": color_searched,
        "total_quantity": total_quantity,  # <-- Add total quantity to context
        "pallet_contents_results": None,  # Ensure this is None when handling product search
        "pallet_searched": None,
    }
    return render(request, "search_key/search_key.html", context)


def search_pallet(request):
    pallet_contents_results = None
    pallet_searched = request.POST.get("search_pallet_number", None)

    if (
        request.method == "POST" and "search_pallet_number" in request.POST
    ):  # Check if pallet form was submitted
        pallet_number = request.POST.get("search_pallet_number")

        pallet_contents = (
            FromsStock.objects.filter(pallet_position=pallet_number, quantity__gt=0)
            .values("product", "color")
            .annotate(total_quantity=Sum("quantity"))
            .order_by("product", "color")
        )
        pallet_contents_results = list(pallet_contents)

    context = {
        "search_results": None,
        "product_searched": None,
        "color_searched": None,
        "total_quantity": 0,  # <-- Also add here, defaulting to 0 for pallet search context
        "pallet_contents_results": pallet_contents_results,
        "pallet_searched": pallet_searched,
    }
    # Render the SAME template
    return render(request, "search_key/search_key.html", context)
