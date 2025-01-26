import phonenumbers

LOCALE = "RU"

def parse_phone(text: str):
    """
    Searches the text for the first valid phone number (according to libphonenumber).
    If found, removes it from the text and returns a tuple (remaining_text, E164_phone_number).
    If no phone number is found, returns False.

    Example:
        "My name is Ivan, number: +7 (999) 123-45-67"
        -> ("My name is Ivan, number:", "+79991234567")
    """

    # Get all potential phone numbers (PhoneNumberMatcher checks formatting, spaces, parentheses, etc.)
    possible_numbers = phonenumbers.PhoneNumberMatcher(text, LOCALE)

    # Take the first match or None if there are no matches
    match = next(possible_numbers, None)
    if not match:
        return False

    # match.raw_string is the substring recognized by libphonenumbers
    # match.start and match.end are the start and end indexes of the phone number in the original text
    start, end = match.start, match.end
    phone_str_raw = match.raw_string

    # Attempt to parse the matched string and check if it's valid
    phone_obj = phonenumbers.parse(phone_str_raw, LOCALE)
    if not phonenumbers.is_valid_number(phone_obj):
        return False

    # Convert to a consistent format (for example, E164 like +79991234567)
    phone_str_formatted = phonenumbers.format_number(
        phone_obj, 
        phonenumbers.PhoneNumberFormat.E164
    )
    
    # Return (formatted_phone_number)
    return phone_str_formatted

def parse_name(text: str):
    # Get all potential phone numbers (PhoneNumberMatcher checks formatting, spaces, parentheses, etc.)
    possible_numbers = phonenumbers.PhoneNumberMatcher(text, LOCALE)

    # Take the first match or None if there are no matches
    match = next(possible_numbers, None)
    if not match:
        return False

    # match.raw_string is the substring recognized by libphonenumbers
    # match.start and match.end are the start and end indexes of the phone number in the original text
    start, end = match.start, match.end
    phone_str_raw = match.raw_string

    # Attempt to parse the matched string and check if it's valid
    phone_obj = phonenumbers.parse(phone_str_raw, LOCALE)
    if not phonenumbers.is_valid_number(phone_obj):
        return False


    # "Remove" the phone number from the original text
    # Take the substring before and after the matched phone number and then strip it
    name_part = (text[:start] + text[end:]).strip()
    
    # Return (remaining_text)
    return name_part

def is_phone_number_exists(text: str):

    # Get all potential phone numbers (PhoneNumberMatcher checks formatting, spaces, parentheses, etc.)
    possible_numbers = phonenumbers.PhoneNumberMatcher(text, "RU")  # "RU" = default region

    # Take the first match or None if there are no matches
    match = next(possible_numbers, None)
    
    if not match:
        return False

    # match.raw_string is the substring recognized by libphonenumbers
    phone_str_raw = match.raw_string

    # Attempt to parse the matched string and check if it's valid
    phone_obj = phonenumbers.parse(phone_str_raw, LOCALE)
    if not phonenumbers.is_valid_number(phone_obj):
        return False    
