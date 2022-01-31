# -*- coding: utf-8 -*-
"""
Sample code for using webexteamsbot
"""

import os
import requests
from webexteamsbot import TeamsBot
from webexteamsbot.models import Response
import sys
import json

# Retrieve required details from environment variables
bot_email = os.getenv("TEAMS_BOT_EMAIL")
teams_token = os.getenv("TEAMS_BOT_TOKEN")
bot_url = os.getenv("TEAMS_BOT_URL")
bot_app_name = os.getenv("TEAMS_BOT_APP_NAME")

# Example: How to limit the approved Webex Teams accounts for interaction
#          Also uncomment the parameter in the instantiation of the new bot
# List of email accounts of approved users to talk with the bot
# approved_users = [
#     "josmith@demo.local",
# ]

# If any of the bot environment variables are missing, terminate the app
if not bot_email or not teams_token or not bot_url or not bot_app_name:
    print(
        "sample.py - Missing Environment Variable. Please see the 'Usage'"
        " section in the README."
    )
    if not bot_email:
        print("TEAMS_BOT_EMAIL")
    if not teams_token:
        print("TEAMS_BOT_TOKEN")
    if not bot_url:
        print("TEAMS_BOT_URL")
    if not bot_app_name:
        print("TEAMS_BOT_APP_NAME")
    sys.exit()

# Create a Bot Object
#   Note: debug mode prints out more details about processing to terminal
#   Note: the `approved_users=approved_users` line commented out and shown as reference
bot = TeamsBot(
    bot_app_name,
    teams_bot_token=teams_token,
    teams_bot_url=bot_url,
    teams_bot_email=bot_email,
    debug=True,
    # approved_users=approved_users,
    webhook_resource_event=[
        {"resource": "messages", "event": "created"},
        {"resource": "attachmentActions", "event": "created"},
    ],
)


# Create a custom bot greeting function returned when no command is given.
# The default behavior of the bot is to return the '/help' command response
def greeting(incoming_msg):
    # Loopkup details about sender
    sender = bot.teams.people.get(incoming_msg.personId)

    # Create a Response object and craft a reply in Markdown.
    response = Response()
    response.markdown = "Hello {}, I'm a chat bot. ".format(sender.firstName)
    response.markdown += "See what I can do by asking for **/help**."
    return response


# Create functions that will be linked to bot commands to add capabilities
# ------------------------------------------------------------------------

# A simple command that returns a basic string that will be sent as a reply
def do_something(incoming_msg):
    """
    Sample function to do some action.
    :param incoming_msg: The incoming message object from Teams
    :return: A text or markdown based reply
    """
    return "i did what you said - {}".format(incoming_msg.text)


def _filter_dict(dict_to_parse: dict, message_params: str):
    """
    filters out keywords based on message contents
    :param dictionary to parse
    :param incoming_msg: The incoming message object from Teams
    :return: A dictionary""" 

    message_keywords = [item.lower() for item in message_params.split()]
    new_dict = {key: dict_to_parse[key]
                for key in dict_to_parse
                if key.lower() in message_keywords}
    if not new_dict:
        return dict_to_parse
    return new_dict
    
def _format_time(time: dict, message_params: str):
    time_template = """{time} : {en1} and {en2}\n"""
    time_out = ""
    time = _filter_dict(time, message_params) if message_params else time
    for t, engineers in time.items():
        en1 = engineers[0] if 0 <= 0 < len(
            engineers) else "No Engineer Assigned"
        en2 = engineers[1] if 0 <= 1 < len(
            engineers) else "No Engineer Assigned"
        time_out += time_template.format(time=t, en1=en1, en2=en2)
    return time_out


def _format_tier(tier: dict, message_params: str):
    # Todo intake message params filter for tier
    tier = _filter_dict(tier, message_params) if message_params else tier
    tier_tempplate = '''The following {tier} engineers are assinged to work:\n'''
    return "".join(
       (tier_tempplate.format(tier=tier.upper()) + _format_time(time, message_params))
        for tier, time in tier.items()
    )


def _format_schedule_msg(sc: dict, message_params: str):
    template = """\
        On date: {date}
        """
    out = ""
    sc = _filter_dict(sc, message_params) if message_params else sc
    # Todo intake message params filter for date
    for date, tier in sc.items():
        out += template.format(date=date)
        out += _format_tier(tier, message_params)

    return out

# A simple command that returns weeks schedule


def show_schedule(incoming_msg):
    """
    Sample function to do some action.
    :param incoming_msg: The incoming message object from Teams
    :return: A text or markdown based reply
    """
    message_params = bot.extract_message(
        "/schedule", incoming_msg.text).strip()

    with open('sample_data.json', 'r') as f:
        sc = json.loads((f.read()))
    return _format_schedule_msg(sc, message_params=message_params)

# This function generates a basic adaptive card and sends it to the user
# You can use Microsofts Adaptive Card designer here:
# https://adaptivecards.io/designer/. The formatting that Webex Teams
# uses isn't the same, but this still helps with the overall layout
# make sure to take the data that comes out of the MS card designer and
# put it inside of the "content" below, otherwise Webex won't understand
# what you send it.


def show_card(incoming_msg):
    attachment = """
    {
        "contentType": "application/vnd.microsoft.card.adaptive",
        "content": {
            "type": "AdaptiveCard",
            "body": [{
                "type": "Container",
                "items": [{
                    "type": "TextBlock",
                    "text": "This is a sample of the adaptive card system."
                }]
            }],
            "actions": [{
                    "type": "Action.Submit",
                    "title": "Create",
                    "data": "add",
                    "style": "positive",
                    "id": "button1"
                },
                {
                    "type": "Action.Submit",
                    "title": "Delete",
                    "data": "remove",
                    "style": "destructive",
                    "id": "button2"
                }
            ],
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "version": "1.0"
        }
    }
    """
    backupmessage = "This is an example using Adaptive Cards."

    c = create_message_with_attachment(
        incoming_msg.roomId, msgtxt=backupmessage, attachment=json.loads(
            attachment)
    )
    print(c)
    return ""


# An example of how to process card actions
def handle_cards(api, incoming_msg):
    """
    Sample function to handle card actions.
    :param api: webexteamssdk object
    :param incoming_msg: The incoming message object from Teams
    :return: A text or markdown based reply
    """
    m = get_attachment_actions(incoming_msg["data"]["id"])

    return "card action was - {}".format(m["inputs"])


# Temporary function to send a message with a card attachment (not yet
# supported by webexteamssdk, but there are open PRs to add this
# functionality)
def create_message_with_attachment(rid, msgtxt, attachment):
    headers = {
        "content-type": "application/json; charset=utf-8",
        "authorization": "Bearer " + teams_token,
    }

    url = "https://api.ciscospark.com/v1/messages"
    data = {"roomId": rid, "attachments": [attachment], "markdown": msgtxt}
    response = requests.post(url, json=data, headers=headers)
    return response.json()


# Temporary function to get card attachment actions (not yet supported
# by webexteamssdk, but there are open PRs to add this functionality)
def get_attachment_actions(attachmentid):
    headers = {
        "content-type": "application/json; charset=utf-8",
        "authorization": "Bearer " + teams_token,
    }

    url = "https://api.ciscospark.com/v1/attachment/actions/" + attachmentid
    response = requests.get(url, headers=headers)
    return response.json()


# An example using a Response object.  Response objects allow more complex
# replies including sending files, html, markdown, or text. Rsponse objects
# can also set a roomId to send response to a different room from where
# incoming message was recieved.
def ret_message(incoming_msg):
    """
    Sample function that uses a Response object for more options.
    :param incoming_msg: The incoming message object from Teams
    :return: A Response object based reply
    """
    # Create a object to create a reply.
    response = Response()

    # Set the text of the reply.
    response.text = "Here's a fun little meme."

    # Craft a URL for a file to attach to message
    u = "https://sayingimages.com/wp-content/uploads/"
    u = u + "aaaaaalll-righty-then-alrighty-meme.jpg"
    response.files = u
    return response


# An example command the illustrates using details from incoming message within
# the command processing.
def current_time(incoming_msg):
    """
    Sample function that returns the current time for a provided timezone
    :param incoming_msg: The incoming message object from Teams
    :return: A Response object based reply
    """
    # Extract the message content, without the command "/time"
    timezone = bot.extract_message("/time", incoming_msg.text).strip()

    # Craft REST API URL to retrieve current time
    #   Using API from http://worldclockapi.com
    u = "http://worldclockapi.com/api/json/{timezone}/now".format(
        timezone=timezone)
    r = requests.get(u).json()

    # If an invalid timezone is provided, the serviceResponse will include
    # error message
    if r["serviceResponse"]:
        return "Error: " + r["serviceResponse"]

    # Format of returned data is "YYYY-MM-DDTHH:MM<OFFSET>"
    #   Example "2018-11-11T22:09-05:00"
    returned_data = r["currentDateTime"].split("T")
    cur_date = returned_data[0]
    cur_time = returned_data[1][:5]
    timezone_name = r["timeZoneName"]

    # Craft a reply string.
    reply = "In {TZ} it is currently {TIME} on {DATE}.".format(
        TZ=timezone_name, TIME=cur_time, DATE=cur_date
    )
    return reply


# Create help message for current_time command
current_time_help = "Look up the current time for a given timezone. "
current_time_help += "_Example: **/time EST**_"

# Set the bot greeting.
bot.set_greeting(greeting)

# Add new commands to the bot.
bot.add_command("attachmentActions", "*", handle_cards)
bot.add_command("/showcard", "show an adaptive card", show_card)
bot.add_command("/dosomething", "help for do something", do_something)
bot.add_command("/schedule", "show this weeks schedule", show_schedule)
bot.add_command(
    "/demo", "Sample that creates a Teams message to be returned.", ret_message
)
bot.add_command("/time", current_time_help, current_time)

# Every bot includes a default "/echo" command.  You can remove it, or any
# other command with the remove_command(command) method.
bot.remove_command("/echo")

if __name__ == "__main__":
    # Run Bot
    bot.run(host="0.0.0.0", port=5000)
