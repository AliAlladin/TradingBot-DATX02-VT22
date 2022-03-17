import sys
import json
import requests

url = "https://hooks.slack.com/services/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"


def sendNotification(message):
    notification = message
    slack_data = {
        "username": "NotBot",
        "icon_emoji": ":robot_face:",
        "attachments": [
            {
                "color": "#9733EE",
                "fields": [
                    {
                        "value": notification,
                        "short": "false",
                    }
                ]
            }
        ]
    }
    byte_length = str(sys.getsizeof(slack_data))
    headers = {'Content-Type': "application/json", 'Content-Length': byte_length}
    response = requests.post(url, data=json.dumps(slack_data), headers=headers)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)