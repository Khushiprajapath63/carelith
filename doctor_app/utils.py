import requests

def send_otp_sms(phone, otp):
    url = "https://www.fast2sms.com/dev/bulkV2"

    payload = {
        "route": "otp",
        "variables_values": otp,
        "numbers": phone
    }

    headers = {
        "authorization": "nSD2B3JxbCycVPqtkEAwNlvIeRLQ0F56UshYfjopOzrGm9gZHaA3jQBkfa2w98SVzXD0hWlR5iYKdrUn",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()
