import requests
import icalendar
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText

# Airbnb iCal URLs for all flats (replace with your own listing's iCal URLs)
ical_urls = {
    "Flat 304": "https://www.airbnb.co.uk/calendar/ical/676174099255535802.ics?s=6850ada59fac492e332802abe712cba2",
    # Add other flats as necessary
}

# Function to fetch and parse iCal data
def fetch_ical_data(url):
    try:
        print("Fetching iCal data...")
        ical_data = requests.get(url).text
        print("iCal data fetched successfully.")
        return ical_data
    except Exception as e:
        print(f"Error fetching iCal data: {e}")
        return None

# Function to extract check-in and check-out events for tomorrow
def get_check_in_out_events(calendar):
    check_in_out_events = {}
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)

    # Loop through calendar events and filter for check-ins and check-outs
    for event in calendar.walk('vevent'):
        start_date = event.get('dtstart').dt
        end_date = event.get('dtend').dt
        summary = event.get('summary')

        # Convert to date if necessary
        if isinstance(start_date, datetime):
            start_date = start_date.date()
        if isinstance(end_date, datetime):
            end_date = end_date.date()

        # Check for check-ins and check-outs tomorrow
        if start_date == tomorrow:
            check_in_out_events[summary] = f"{summary}: Check-in"
        if end_date == tomorrow:
            if summary in check_in_out_events:
                check_in_out_events[summary] += " / OUT"
            else:
                check_in_out_events[summary] = f"{summary}: OUT"

    return check_in_out_events

# Function to send email
def send_email(message):
    sender_email = "hasanuot@gmail.com"  # Replace with your email
    sender_password = "awceaeimpbzdboxx"  # Replace with your email password
    recipient_email = "hasanalshammaa@gmail.com"  # Replace with recipient's email

    msg = MIMEText(message)
    msg['Subject'] = "Daily Check-in/Check-out Notification"
    msg['From'] = sender_email
    msg['To'] = recipient_email

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
            print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Main execution block
message = ""
for flat, url in ical_urls.items():
    ical_data = fetch_ical_data(url)
    if ical_data:
        try:
            calendar = icalendar.Calendar.from_ical(ical_data)
            check_in_out_events = get_check_in_out_events(calendar)

            # Build the message for each flat
            if check_in_out_events:
                if not message:
                    message += f"DAY AND DATE: {datetime.now().date() + timedelta(days=1)}\n"
                for summary, event in check_in_out_events.items():
                    flat_number = summary.split(":")[0]  # Extract flat number from summary
                    if "Check-in" in event and "OUT" in event:
                        message += f"{flat_number} OUT-IN\n"
                    elif "Check-in" in event:
                        message += f"{flat_number} IN\n"
                    elif "OUT" in event:
                        message += f"{flat_number} OUT\n"
            else:
                message += f"{flat}: No events today.\n"
        except Exception as e:
            print(f"Error parsing iCal data for {flat}: {e}")

# Output the final message
if message:
    print(message)
    send_email(message)
else:
    print("No Check-ins or Check-outs tomorrow for any flats.")

