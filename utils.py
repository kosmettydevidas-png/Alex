# Utility Functions for the Chatbot

def get_current_datetime():
    """
    Returns the current date and time in UTC.
    """
    from datetime import datetime
    return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')


def format_response(response):
    """
    Formats the chatbot response for better readability.
    """
    return f'Response: {response}'


def log_message(message):
    """
    Logs a message with a timestamp.
    """
    from datetime import datetime
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    print(f'[{timestamp}] {message}')