import phonenumbers

LOCALE = "RU"

def parse_phone(text: str):
    """
    Searches the text for the first valid phone number (according to libphonenumbers).
    If found, returns the number in E164 format (e.g., +79991234567).
    If no phone number is found, returns False.
    """

    # Get a PhoneNumberMatcher object
    possible_numbers = phonenumbers.PhoneNumberMatcher(text, LOCALE)

    # Use a for-loop to get the first match
    match = None
    for candidate in possible_numbers:
        match = candidate
        break

    if not match:
        return False

    start, end = match.start, match.end
    phone_str_raw = match.raw_string

    phone_obj = phonenumbers.parse(phone_str_raw, LOCALE)
    if not phonenumbers.is_valid_number(phone_obj):
        return False

    # Convert to a consistent format (for example, E164 like +79991234567)
    phone_str_formatted = phonenumbers.format_number(
        phone_obj, 
        phonenumbers.PhoneNumberFormat.E164
    )
    
    return phone_str_formatted

def parse_name(text: str):
    """
    Searches the text for the first valid phone number and removes it from the text.
    Returns the remaining text (interpreted as "name part") or False if no valid number found.
    """
    possible_numbers = phonenumbers.PhoneNumberMatcher(text, LOCALE)

    match = None
    for candidate in possible_numbers:
        match = candidate
        break

    if not match:
        return False

    start, end = match.start, match.end
    phone_str_raw = match.raw_string

    phone_obj = phonenumbers.parse(phone_str_raw, LOCALE)
    if not phonenumbers.is_valid_number(phone_obj):
        return False

    # Remove the matched phone substring from the text
    name_part = (text[:start] + text[end:]).strip()
    return name_part

def is_phone_number_exists(text: str):
    """
    Returns True if there's at least one valid phone number in the text, otherwise False.
    """
    possible_numbers = phonenumbers.PhoneNumberMatcher(text, LOCALE)

    match = None
    for candidate in possible_numbers:
        match = candidate
        break

    if not match:
        return False

    phone_str_raw = match.raw_string
    phone_obj = phonenumbers.parse(phone_str_raw, LOCALE)

    return phonenumbers.is_valid_number(phone_obj)  
