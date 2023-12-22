import logging
import urllib.request
import urllib.parse
import urllib.error
import json
import re
import os
from datetime import datetime
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import BotoCoreError, ClientError
import time
from vars import *


TELEGRAM_API_KEY = os.environ['TELEGRAM_API_KEY']
TELEGRAM_BOT_API = f"https://api.telegram.org/bot{TELEGRAM_API_KEY}/"
DYNAMODB_TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME')
START_COMMAND = '/start'
ABOUT_COMMAND = '/about'
HELP_COMMAND = '/help'
DUMMY_DATE = '1900-01-01'

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Create a DynamoDB resource
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(DYNAMODB_TABLE_NAME)


def send_telegram_api_request(operation, data, headers=None):
    """
    Function to send HTTP request to Telegram API
    :param operation: API operation endpoint
    :param data: Data to send in the body of the request, in dictionary form
    :param headers: Any headers to include in the request, in dictionary form
    :returns: Dictionary containing server's response
    :raises Exception: If any errors occur during the HTTP request
    """
    url = f"{TELEGRAM_BOT_API}{operation}"
    data = json.dumps(data).encode("utf-8")
    if not headers:
        headers = {"Content-Type": "application/json"}
    try:
        request = urllib.request.Request(url, data, headers)
        response = urllib.request.urlopen(request).read().decode("utf-8")
        return json.loads(response)
    except urllib.error.HTTPError as error:
        logger.error(error.reason)
        return {"error": str(error.reason)}
    except urllib.error.URLError as error:
        logger.error(error.reason)
        return {"error": str(error.reason)}
    except TimeoutError:
        logger.error("Request timed out")
        return {"error": "Request timed out"}


def create_data_dictionary(chat_id, text, message_id=None, reply_markup=None, parse_mode=None):
    """
    Create a dictionary for data to be sent in a request.
    :param chat_id: ID of chat
    :param text: The text to be sent
    :param message_id: Optional ID of the message. Default is None.
    :param reply_markup: Optional markup settings. Default is None.
    :param parse_mode: Optional parse mode settings. Default is None.
    :return: Dictionary containing the data
    """
    data = {
        "chat_id": chat_id,
        "text": text
    }
    if message_id:
        data["message_id"] = message_id
    if reply_markup:
        data["reply_markup"] = reply_markup
    if parse_mode:
        data["parse_mode"] = parse_mode
    return data


def send_message(chat_id, text, reply_markup=None, parse_mode=None):
    data = create_data_dictionary(chat_id, text, reply_markup=reply_markup, parse_mode=parse_mode)
    return send_telegram_api_request("sendMessage", data)


def send_editMessageText(chat_id, message_id, text, reply_markup=None, parse_mode=None):
    data = create_data_dictionary(chat_id, text, message_id=message_id, reply_markup=reply_markup, parse_mode=parse_mode)
    return send_telegram_api_request("editMessageText", data)


def send_answerCallbackQuery(callback_query_id, text=None, show_alert=False):
    """
    Sends an answer to a callback query.
    :param callback_query_id: The ID of the the callback query to answer.
    :param text: Optional; the text to send in the answer. Defaults to None.
    :param show_alert: Optional; determines whether an alert will be shown. Defaults to False.
    :return: Response from the sendRequest function
    """
    data = {
        "callback_query_id": callback_query_id
    }
    if text:
        data["text"] = text
        data["show_alert"] = show_alert
    return send_telegram_api_request("answerCallbackQuery", data)


def message_data_encode(text, data_to_encode):
    """
    Encodes data into a message using zero-space link method from stateless-question library.
    :param text: The original text of the message.
    :param data_to_encode: The data to encode into the text.
    :return: An encoded message string.
    """
    zerowidth_character = "\u200C"
    base_url = "https://t.me/?encoded="
    encoded_url = base_url + urllib.parse.quote_plus(data_to_encode)
    html_markup = f"<a href=\"{encoded_url}\">{zerowidth_character}</a>"
    text = str(text) + html_markup
    return text


def message_data_decode(text):
    """
    Decodes data from a message.
    :param text: The text of the message.
    :return: Decoded data from the input message.
    """
    regex = r"https\:\/\/t\.me\/\?encoded\=(.*)"
    result = re.findall(regex, text)
    if result and result[0]:
        return urllib.parse.unquote_plus(result[0])
    else:
        return None


def delete_trip(user_id, trip_id):
    """
    Deletes a trip for a user from the DynamoDB table
    :param user_id: the ID of the user
    :param trip_id: the ID of the trip
    :return: response from DynamoDB
    """
    try:
        response = table.delete_item(Key={'user_id': user_id, 'trip_id': trip_id})
        return response
    except (BotoCoreError, ClientError) as error:
        logger.error(f"Failed to delete trip: {error}")


def save_trip_data(user_id, trip_data):
    """
    Saves trip data for a user into DynamoDB table
    :param user_id: the ID of the user
    :param trip_data: the data of the trip
    :return: response from DynamoDB
    """
    trip_data['user_id'] = user_id
    trip_data["dummy_partition_key"] = "constant"
    try:
        response = table.put_item(Item=trip_data)
        return response
    except Exception as e:
        logger.error(f'Failed to save item to DynamoDB: {str(e)}')


def get_my_trips(user_id):
    """
    Queries DynamoDB for the trips of a specific user
    :param user_id: the ID of the user
    :return: list of trips of the user
    """
    try:
        response = table.query(
            KeyConditionExpression=Key('user_id').eq(int(user_id))
        )
        return response['Items']
    except (BotoCoreError, ClientError) as error:
        logger.error(f"Failed to query trips: {error}")


def get_trips(is_to_belarus, yyyy, mm):
    """
    Queries DynamoDB for trips during a specific month and year
    :param is_to_belarus: boolean if trips are to Belarus
    :param yyyy: the year of the trip
    :param mm: the month of the trip
    :return: list of trips during the specific month
    """
    # Convert the user-provided year and month to a timestamp range.
    from_date = datetime.strptime(f"{yyyy}-{mm}-01", "%Y-%m-%d")
    try:
        if mm == 12:
            to_date = datetime.strptime(f"{str(int(yyyy) + 1)}-01-01", "%Y-%m-%d")
        else:
            to_date = datetime.strptime(f"{yyyy}-{str(int(mm) + 1)}-01", "%Y-%m-%d")
        # Define the key condition expression for querying DynamoDB.
        if is_to_belarus:  # If interested in trip to Belarus
            index_name = 'to_belarus_date-index'
            key_condition = Key('dummy_partition_key').eq('constant') & \
                            Key('to_belarus_date').between(str(from_date), str(to_date))
        else:  # If interested in trip to Spain
            index_name = 'to_spain_date-index'
            key_condition = Key('dummy_partition_key').eq('constant') & \
                            Key('to_spain_date').between(str(from_date), str(to_date))
        # Query DynamoDB.
        response = table.query(
            IndexName=index_name,
            KeyConditionExpression=key_condition
        )
        return response['Items']
    except (BotoCoreError, ClientError, ValueError) as error:
        logger.error(f"Failed to get trips: {error}")


def parse_date(date_string):
    try:
        # Try to convert the string to a date object.
        # Assume the user should enter the date in the format "DD-MM-YYYY"
        return datetime.strptime(date_string, "%d-%m-%Y").date()
    except ValueError:
        # If conversion fails, it's not a valid date.
        return None


def parse_date_to_ym(date_string):
    try:
        # Try to convert the string to a date object.
        # Assume the user should enter the date in the format "MM-YYYY"
        parsed_date = datetime.strptime(date_string, "%m-%Y")
        return [parsed_date.strftime("%Y"), parsed_date.strftime("%m")]
    except ValueError:
        # If conversion fails, it's not a valid date.
        return None


def generate_get_trips_msg(user_id):
    """
    Generates a message for user's trips. It fetches user trips and formats a message with trip details.
    It also appends a delete button to the inline keyboard object for each trip.

    :param user_id: the ID of the user
    :return: List with message text and inline keyboard dict
    """
    trips = get_my_trips(user_id)
    if not trips:
        getmytrips_text = "У вас нет предстоящих поездок"
    else:
        getmytrips_text = "Вот ваши предстоящие поездки:\n\n"
        for i, trip in enumerate(trips, start=1):
            if trip["to_belarus_date"] == DUMMY_DATE:
                trip["to_belarus_date"] = "-"
            if trip["to_spain_date"] == DUMMY_DATE:
                trip["to_spain_date"] = "-"
            getmytrips_text += f"{i}. " \
                               f"Ваш контакт, как он отобразится в поиске: <a href=\"tg://user?id={trip['user_id']}\">{trip['first_name']}</a>,\n" \
                               f"Дата поездки в Беларусь: {trip['to_belarus_date']},\n" \
                               f"Дата поездки в Испанию: {trip['to_spain_date']},\n" \
                               f"Примечание: {trip['note']}\n\n"
            button = [{f"text": f"Удалить поездку {i}.", "callback_data": f"/deletetrip_{trip['trip_id']}"}]
            GETMYTRIPS_INLINE_KEYBOARD["inline_keyboard"].insert(i - 1, button)
    return getmytrips_text, GETMYTRIPS_INLINE_KEYBOARD


def handle_startcallback(chat_id, message_id):
    send_editMessageText(chat_id, message_id, GREETING_TEXT, reply_markup=GREETING_INLINE_KEYBOARD)


def handle_searchtrips(chat_id, message_id):
    send_editMessageText(chat_id, message_id, SEARCH_INTRO_TEXT, reply_markup=SEARCH_INTRO_INLINE_KEYBOARD)


def handle_searchbelarusdate(chat_id):
    send_message(chat_id, SEARCH_BELARUS_TIME_TEXT, reply_markup={"force_reply": True})


def handle_searchspaindate(chat_id):
    send_message(chat_id, SEARCH_SPAIN_TIME_TEXT, reply_markup={"force_reply": True})


def handle_savetrip(chat_id):
    send_message(chat_id, SAVETRIP_STEP1_TEXT, reply_markup={"force_reply": True})


def handle_getmytrips(chat_id, user_id, message_id):
    text, inline_keyboard = generate_get_trips_msg(user_id)
    send_editMessageText(chat_id, message_id, text, reply_markup=inline_keyboard, parse_mode="HTML")


def handle_deletetrip(callback_query_data, chat_id, user_id, message_id):
    trip_id = callback_query_data.split("_")[1]
    delete_trip(user_id, trip_id)
    text, inline_keyboard = generate_get_trips_msg(user_id)
    send_editMessageText(chat_id, message_id, text, reply_markup=inline_keyboard, parse_mode="HTML")


def handle_callback_query(update):
    callback_query = update['callback_query']
    callback_query_id = callback_query['id']
    callback_query_data = callback_query['data']
    message = callback_query['message']
    message_id = message['message_id']
    chat_id = message['chat']['id']
    user_id = callback_query['from']['id']

    logger.debug("callback update fields:")
    for key in update.keys():
        logger.debug(f"{key}: {update[key]}\n")
    logger.debug("callback_query fields:")
    for key in callback_query.keys():
        logger.debug(f"{key}: {callback_query[key]}\n")

    if callback_query_data == START_COMMAND:
        handle_startcallback(chat_id, message_id)
    elif callback_query_data == "/searchtrips":
        handle_searchtrips(chat_id, message_id)
    elif callback_query_data == "/searchbelarusdate":
        handle_searchbelarusdate(chat_id)
    elif callback_query_data == "/searchspaindate":
        handle_searchspaindate(chat_id)
    elif callback_query_data == "/savetrip":
        handle_savetrip(chat_id)
    elif callback_query_data == "/getmytrips":
        handle_getmytrips(chat_id, user_id, message_id)
    elif callback_query_data.startswith("/deletetrip_"):
        handle_deletetrip(callback_query_data, chat_id, user_id, message_id)
    else:
        send_answerCallbackQuery(callback_query_id, text="Something went wrong", show_alert=True)
        logger.error("Unknown callback")
        raise Exception
    send_answerCallbackQuery(callback_query_id)


def handle_start(chat_id):
    send_message(chat_id, GREETING_TEXT, reply_markup=GREETING_INLINE_KEYBOARD)


def handle_about(chat_id):
    send_message(chat_id, ABOUT_TEXT)
    send_message(chat_id, ABOUT_SECOND_MSG_TEXT)


def handle_help(chat_id):
    send_message(chat_id, HELP_TEXT)


def generate_search_results_text(search_results):
    search_results_formatted = ''
    for i, trip in enumerate(search_results, start=1):
        if trip["to_belarus_date"] == DUMMY_DATE:
            trip["to_belarus_date"] = "-"
        if trip["to_spain_date"] == DUMMY_DATE:
            trip["to_spain_date"] = "-"
        search_results_formatted += f"{i}. " \
                                    f"<a href=\"tg://user?id={trip['user_id']}\">{trip['first_name']}</a>,\n" \
                                    f"Дата поездки в Беларусь: {trip['to_belarus_date']},\n" \
                                    f"Дата поездки в Испанию: {trip['to_spain_date']},\n" \
                                    f"Примечание: {trip['note']}\n\n"
    return search_results_formatted


def handle_search(message, chat_id, is_to_belarus=True):
    user_input = message["text"]
    yyyy_mm = parse_date_to_ym(user_input)
    if yyyy_mm:
        search_results = get_trips(is_to_belarus, yyyy_mm[0], yyyy_mm[1])
        if search_results:
            search_results = generate_search_results_text(search_results)
        else:
            search_results = "К сожалению, в этом месяце никто не едет."
        send_message(chat_id, search_results, reply_markup=SEARCH_END_KEYBOARD, parse_mode="HTML")
    else:
        send_message(chat_id, INCORRECT_SEARCH_DATE_TEXT, reply_markup=SEARCH_END_KEYBOARD)


def handle_savetrip_first_step(chat_id, user_input):
    if user_input == "-" or parse_date(user_input):
        to_belarus_date = DUMMY_DATE if user_input == "-" else str(parse_date(user_input))
        trip_data = json.dumps({"to_belarus_date": to_belarus_date})
        savetrip_step2_text_encoded = message_data_encode(SAVETRIP_STEP2_TEXT, trip_data)
        send_message(chat_id, savetrip_step2_text_encoded, reply_markup={"force_reply": True},
                     parse_mode="HTML")
    else:
        send_message(chat_id, INCORRECT_DATE_TEXT, reply_markup=INCORRECT_DATE_INLINE_KEYBOARD)


def handle_savetrip_second_step(chat_id, message, user_input):
    trip_data = json.loads(message_data_decode(message["reply_to_message"]["entities"][0]["url"]))
    if user_input == "-" or parse_date(user_input):
        to_spain_date = DUMMY_DATE if user_input == "-" else str(parse_date(user_input))
        trip_data["to_spain_date"] = to_spain_date
        trip_data = json.dumps(trip_data)
        savetrip_step3_text_encoded = message_data_encode(SAVETRIP_STEP3_TEXT, trip_data)
        send_message(chat_id, savetrip_step3_text_encoded, reply_markup={"force_reply": True},
                     parse_mode="HTML")
    else:
        send_message(chat_id, INCORRECT_DATE_TEXT, reply_markup=INCORRECT_DATE_INLINE_KEYBOARD)


def handle_savetrip_third_step(chat_id, message, user_id, first_name, user_input):
    trip_data = json.loads(message_data_decode(message["reply_to_message"]["entities"][0]["url"]))
    trip_data["note"] = user_input
    trip_data["first_name"] = first_name
    trip_data["trip_id"] = str(time.time())
    save_trip_data(user_id, trip_data)
    send_message(chat_id, SAVE_SUCCESS_TEXT, reply_markup=SAVE_SUCCESS_INLINE_KEYBOARD)


def generic_error_response(chat_id):
    send_message(chat_id, GENERIC_ERROR_TEXT)


def handle_text_message(update):
    message = update['message']
    chat_id = message['chat']['id']
    user_input = message['text']
    user_id = message['from']['id']
    first_name = message['from']['first_name']

    logger.debug("Message Fields:")
    for key in message.keys():
        logger.debug(f"{key}: {message[key]}\n")
    logger.debug("Update Fields:")
    for key in update.keys():
        logger.debug(f"{key}: {update[key]}\n")

    if user_input.lower() == START_COMMAND:
        handle_start(chat_id)
    elif user_input.lower() == ABOUT_COMMAND:
        handle_about(chat_id)
    elif user_input.lower() == HELP_COMMAND:
        handle_help(chat_id)

    else:
        if "reply_to_message" in message:
            reply_message_text = message["reply_to_message"]["text"]
            if reply_message_text == SAVETRIP_STEP1_TEXT:
                handle_savetrip_first_step(chat_id, user_input)
            elif reply_message_text.startswith(SAVETRIP_STEP2_TEXT):
                handle_savetrip_second_step(chat_id, message, user_input)
            elif reply_message_text.startswith(SAVETRIP_STEP3_TEXT):
                handle_savetrip_third_step(chat_id, message, user_id, first_name, user_input)
            elif reply_message_text == SEARCH_BELARUS_TIME_TEXT:
                handle_search(message, chat_id, is_to_belarus=True)
            elif reply_message_text == SEARCH_SPAIN_TIME_TEXT:
                handle_search(message, chat_id, is_to_belarus=False)
        else:
            logger.info('Incorrect input')
            generic_error_response(chat_id)


def process_update(update):
    if 'callback_query' in update:
        handle_callback_query(update)
    else:
        handle_text_message(update)


def lambda_handler(event, context):
    '''
    The Lambda function handler. Processes an incoming event and passes the event body to process_update() method

    :param event: The incoming event data
    :param context: The Lambda context object.
    :return: dict: A dictionary containing HTTP response code and body.
        Always returns 200 to make sure that agent won't spam to server
    '''
    event_processed = {"statusCode": 200, "body": json.dumps({})}
    try:
        update = json.loads(event['body'])
        process_update(update)
        return event_processed
    except Exception as E:
        logger.error("Something went terribly wrong. Bot crashed")
        logger.error(E)
        return event_processed
