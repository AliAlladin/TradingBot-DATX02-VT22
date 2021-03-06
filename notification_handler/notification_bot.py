import json

import requests
import sys

# Replace with the generated webhock URL. Not to be published online.
url = "___________________________________________________________"


def send_notification(message):
    """
    This method is responsible for sending out messages to a channel in Slack, specified by a specific URL-address.
    :param message: The message which is to be sent
    :return: returns a error message if the message could not be sent
    """
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
