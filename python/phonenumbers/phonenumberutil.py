# Copyright (C) 2010 Neil Rahilly <neilrahilly@gmail.com>
# 
# Licensed under the Apache License, Version 2.0 (the "License")
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
# http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Utility for international phone numbers.

Functionality includes formatting, parsing and validation. (Based on the Java
implementation.)
"""

import os.path
import re
import cStringIO as StringIO

from phonenumbers import metadata_gen
from phonenumbers import phonemetadata_pb2
from phonenumbers import phonenumber_pb2

COUNTRY_CODE_TO_REGION_CODE_MAP_NAME = "country_code_to_region_code_map"


class Error(Exception):
    pass


class NumberParseError(Error):
    """Errors encountered when parsing phone numbers."""
    INVALID_COUNTRY_CODE = u"Invalid country code"

    # This generally indicates the string passed in had less than 3 digits in
    # it. More specifically, the number failed to match the regular expression
    # VALID_PHONE_NUMBER in PhoneNumberUtil.java.
    NOT_A_NUMBER = u"The string supplied did not seem to be a phone number"

    # This indicates the string started with an international dialing prefix,
    # but after this was stripped from the number, had less digits than any
    # valid phone number (including country code) could have.
    TOO_SHORT_AFTER_IDD = u"Phone number too short after IDD"
    
    # This indicates the string, after any country code has been stripped, had
    # less digits than any valid phone number could have.
    TOO_SHORT_NSN = u"The string supplied is too short to be a phone number"

    # This indicates the string had more digits than any valid phone number
    # could have.
    TOO_LONG = u"The string supplied is too long to be a phone number"

    def __init__(self, error_type, detail):
        error_type = error_type
        detail = detail

    def __str__(self):
        if not self.detail:
            return self.error_type
        return u"%s: %s" (self.error_type, self.detail)


# The minimum length of the national significant number.
_MIN_LENGTH_FOR_NSN = 3

# The maximum length of the national significant number.
_MAX_LENGTH_FOR_NSN = 15

META_DATA_FILE_PREFIX = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), "data",
    "phonenumbermetadataproto")

_file_prefix = META_DATA_FILE_PREFIX


def set_file_prefix(file_prefix):
    global _file_prefix
    _file_prefix = file_prefix

_NANPA_COUNTRY_CODE = 1

# The PLUS_SIGN signifies the international prefix.
PLUS_SIGN = u"+"

# These mappings map a character (key) to a specific digit that should replace
# it for normalization purposes. Non-European digits that may be used in phone
# numbers are mapped to a European equivalent.
DIGIT_MAPPINGS = {
    u"0": u"0",
    u"1": u"1",
    u"2": u"2",
    u"3": u"3",
    u"4": u"4",
    u"5": u"5",
    u"6": u"6",
    u"7": u"7",
    u"8": u"8",
    u"9": u"9",
    u"\uFF10": u"0", # Fullwidth digit 0
    u"\uFF11": u"1", # Fullwidth digit 1
    u"\uFF12": u"2", # Fullwidth digit 2
    u"\uFF13": u"3", # Fullwidth digit 3
    u"\uFF14": u"4", # Fullwidth digit 4
    u"\uFF15": u"5", # Fullwidth digit 5
    u"\uFF16": u"6", # Fullwidth digit 6
    u"\uFF17": u"7", # Fullwidth digit 7
    u"\uFF18": u"8", # Fullwidth digit 8
    u"\uFF19": u"9", # Fullwidth digit 9
    u"\u0660": u"0", # Arabic-indic digit 0
    u"\u0661": u"1", # Arabic-indic digit 1
    u"\u0662": u"2", # Arabic-indic digit 2
    u"\u0663": u"3", # Arabic-indic digit 3
    u"\u0664": u"4", # Arabic-indic digit 4
    u"\u0665": u"5", # Arabic-indic digit 5
    u"\u0666": u"6", # Arabic-indic digit 6
    u"\u0667": u"7", # Arabic-indic digit 7
    u"\u0668": u"8", # Arabic-indic digit 8
    u"\u0669": u"9", # Arabic-indic digit 9
}

# Only upper-case variants of alpha characters are stored.
_ALPHA_MAPPINGS = {
    u"A": u"2",
    u"B": u"2",
    u"C": u"2",
    u"D": u"3",
    u"E": u"3",
    u"F": u"3",
    u"G": u"4",
    u"H": u"4",
    u"I": u"4",
    u"J": u"5",
    u"K": u"5",
    u"L": u"5",
    u"M": u"6",
    u"N": u"6",
    u"O": u"6",
    u"P": u"7",
    u"Q": u"7",
    u"R": u"7",
    u"S": u"7",
    u"T": u"8",
    u"U": u"8",
    u"V": u"8",
    u"W": u"9",
    u"X": u"9",
    u"Y": u"9",
    u"Z": u"9",
}

# For performance reasons, amalgamate both into one map.
# TODO: Does this apply in Python?
_ALL_NORMALIZATION_MAPPINGS = {}
_ALL_NORMALIZATION_MAPPINGS.update(DIGIT_MAPPINGS)
_ALL_NORMALIZATION_MAPPINGS.update(_ALPHA_MAPPINGS)
 
# A list of all country codes where national significant numbers (excluding any
# national prefix) exist that start with a leading zero.
_LEADING_ZERO_COUNTRIES = frozenset([
    39,  # Italy
    47,  # Norway
    225, # Cote d'Ivoire
    227, # Niger
    228, # Togo
    241, # Gabon
    242, # Congo (Rep. of the)
    268, # Swaziland
    379, # Vatican City
    501, # Belize
])

# Pattern that makes it easy to distinguish whether a country has a unique
# international dialing prefix or not. If a country has a unique international
# prefix (e.g. 011 in USA), it will be represented as a string that contains a
# sequence of ASCII digits. If there are multiple available international
# prefixes in a country, they will be represented as a regex string that always
# contains character(s) other than ASCII digits. Note this regex also includes
# tilde, which signals waiting for the tone.
_UNIQUE_INTERNATIONAL_PREFIX = re.compile(
    u"[\\d]+(?:[~\u2053\u223C\uFF5E][\\d]+)?")

# Regular expression of acceptable punctuation found in phone numbers. This
# excludes punctuation found as a leading character only. This consists of dash
# characters, white space characters, full stops, slashes, square brackets,
# parentheses and tildes. It also includes the letter 'x' as that is found as a
# placeholder for carrier information in some phone numbers.

# FIXME: Made this work by making the range start x- instead of -x
# Otherwise, was getting a sre_constants.error: bad character range
_VALID_PUNCTUATION = (
    u"x-\u2010-\u2015\u2212\u30FC\uFF0D-\uFF0F " +
    u"\u00A0\u200B\u2060\u3000()\uFF08\uFF09\uFF3B\uFF3D.\\[\\]/~\u2053\u223C\uFF5E")

# Digits accepted in phone numbers
_VALID_DIGITS = u"".join(set(DIGIT_MAPPINGS.keys()))

# We accept alpha characters in phone numbers, ASCII only, upper and lower case.
_VALID_ALPHA = u"".join(set(
    _ALPHA_MAPPINGS.keys() + [k.lower() for k in _ALPHA_MAPPINGS.keys()]))
_PLUS_CHARS = u"+\uFF0B"
_PLUS_CHARS_PATTERN = re.compile(u"[" + _PLUS_CHARS + u"]+")
_CAPTURING_DIGIT_PATTERN = re.compile(u"([" + _VALID_DIGITS + u"])")

# Regular expression of acceptable characters that may start a phone number for
# the purposes of parsing. This allows us to strip away meaningless prefixes to
# phone numbers that may be mistakenly given to us. This consists of digits,
# the plus symbol and arabic-indic digits. This does not contain alpha
# characters, although they may be used later in the number. It also does not
# include other punctuation, as this will be stripped later during parsing and
# is of no information value when parsing a number.
_VALID_START_CHAR = u"[" + _PLUS_CHARS + _VALID_DIGITS + u"]"
VALID_START_CHAR_PATTERN = re.compile(_VALID_START_CHAR)
 
# Regular expression of characters typically used to start a second phone
# number for the purposes of parsing. This allows us to strip off parts of the
# number that are actually the start of another number, such as for:
# (530) 583-6985 x302/x2303 -> the second extension here makes this actually
# two phone numbers, (530) 583-6985 x302 and (530) 583-6985 x2303. We remove
# the second extension so that the first number is parsed correctly.
_SECOND_NUMBER_START = u"[\\\\/] *x"
_SECOND_NUMBER_START_PATTERN = re.compile(_SECOND_NUMBER_START)

# Regular expression of trailing characters that we want to remove. We remove
# all characters that are not alpha or numerical characters. The hash character
# is retained here, as it may signify the previous block was an extension.
_UNWANTED_END_CHAR_PATTERN = re.compile(
    u"[^" + 
    _VALID_DIGITS +
    _VALID_ALPHA + 
    u"#]+$"
)

# We use this pattern to check if the phone number has at least three letters
# in it - if so, then we treat it as a number where some phone-number digits
# are represented by letters.
_VALID_ALPHA_PHONE_PATTERN = re.compile(u"(?:.*?[A-Za-z]){3}.*")

# Regular expression of viable phone numbers. This is location independent.
# Checks we have at least three leading digits, and only valid punctuation,
# alpha characters and digits in the phone number. Does not include extension
# data. The symbol 'x' is allowed here as valid punctuation since it is often
# used as a placeholder for carrier codes, for example in Brazilian phone
# numbers. We also allow multiple '+' characters at the start.
# Corresponds to the following:
# plus_sign*([punctuation]*[digits]){3,}([punctuation]|[digits]|[alpha])*
_VALID_PHONE_NUMBER = (
    u"[" + 
    _PLUS_CHARS + 
    u"]*(?:[" + 
    _VALID_PUNCTUATION + 
    u"]*[" + 
    _VALID_DIGITS + 
    u"]){3,}[" +
    _VALID_ALPHA + 
    _VALID_PUNCTUATION + 
    _VALID_DIGITS + 
    u"]*"
)

# Default extension prefix to use when formatting. This will be put in front of
# any extension component of the number, after the main national number is
# formatted. For example, if you wish the default extension formatting to be
# ' extn: 3456', then you should specify ' extn: ' here as the default
# extension prefix. This can be overridden by country-specific preferences.
DEFAULT_EXTN_PREFIX_ = u" ext. "

# Regexp of all possible ways to write extensions, for use when parsing. This
# will be run as a case-insensitive regexp match. Wide character versions are
# also provided after each ascii version. There are two regular expressions
# here: the more generic one starts with optional white space and ends with an
# optional full stop (.), followed by zero or more spaces/tabs and then the
# numbers themselves. The other one covers the special case of American numbers
# where the extension is written with a hash at the end, such as "- 503#". Note
# that the only capturing groups should be around the digits that you want to
# capture as part of the extension, or else parsing will fail! We allow two
# options for representing the accented o - the character itself, and one in
# the unicode decomposed form with the combining acute accent.
_KNOWN_EXTN_PATTERNS = (
    u"[ \u00A0\\t,]*" +
    u"(?:ext(?:ensi(?:o\u0301?|\u00F3))?n?|" +
    u"\uFF45\uFF58\uFF54\uFF4E?|[,x\uFF58#\uFF03~\uFF5E]|int|anexo|\uFF49\uFF4E\uFF54)" +
    u"[:\\.\uFF0E]?[ \u00A0\\t,-]*([" + 
    _VALID_DIGITS + 
    u"]{1,7})#?|[- ]+(["+ 
    _VALID_DIGITS +
    u"]{1,5})#"
)

# Regexp of all known extension prefixes used by different countries followed
# by 1 or more valid digits, for use when parsing.
_EXTN_PATTERN = re.compile(
    u"(?:" + _KNOWN_EXTN_PATTERNS + u")$",
    re.UNICODE | re.IGNORECASE)

# We append optionally the extension pattern to the end here, as a valid phone
# number may have an extension prefix appended, followed by 1 or more digits.
_VALID_PHONE_NUMBER_PATTERN = re.compile(
    _VALID_PHONE_NUMBER + u"(?:" + _KNOWN_EXTN_PATTERNS + u")?",
    re.UNICODE | re.IGNORECASE)

_NON_DIGITS_PATTERN = re.compile(u"(\\D+)")
_FIRST_GROUP_PATTERN = re.compile(u"(\\$1)")
_NP_PATTERN = re.compile(u"\\$NP")
_FG_PATTERN = re.compile(u"\\$FG")
_CC_PATTERN = re.compile(u"\\$CC")


# A mapping from a region code to the PhoneMetadata for that region.
_country_to_metadata_map = {}


class _RegexCache(object):
    def __init__(self, size):
        self.size = size
        self._data = {}
        self._history = []

    def get(self, key):
        return self._data.get(key)

    def put(self, key, value):
        self._data[key] = value
        self._history.append(key)
        # LRU strategy
        if len(self._history) > self.size:
            del self._data[self._history.pop(0)]

    def contains_key(self, key):
        return key in self._data


# A cache for frequently used country-specific regular expressions.  As most
# people use phone numbers primarily from one to two countries, and there are
# roughly 60 regular expressions needed, the initial capacity of 100 offers a
# rough load factor of 0.75.
_regex_cache = _RegexCache(100)


# INTERNATIONAL and NATIONAL formats are consistent with the definition in
# ITU-T Recommendation E. 123. For example, the number of the Google Zurich
# office will be written as "+41 44 668 1800" in INTERNATIONAL format, and as
# "044 668 1800" in NATIONAL format. E164 format is as per INTERNATIONAL format
# but with no formatting applied, e.g. +41446681800.
FORMAT_E164 = 0
FORMAT_INTERNATIONAL = 1
FORMAT_NATIONAL = 2

TYPE_FIXED_LINE = 0
TYPE_MOBILE = 1
# In some countries (e.g. the USA), it is impossible to distinguish between
# fixed-line and mobile numbers by looking at the phone number it
TYPE_FIXED_LINE_OR_MOBILE = 2
# Freephone lines
TYPE_TOLL_FREE = 3
TYPE_PREMIUM_RATE = 4
# The cost of this call is shared between the caller and the recipient, and
# is hence typically less than PREMIUM_RATE calls. See
# http:#en.wikipedia.org/wiki/Shared_Cost_Service for more information.
TYPE_SHARED_COST = 5
# Voice over IP numbers. This includes TSoIP (Telephony Service over IP).
TYPE_VOIP = 6
# A personal number is associated with a particular person, and may be routed
# to either a MOBILE or FIXED_LINE number. Some more information can be found
# here: http:#en.wikipedia.org/wiki/Personal_Numbers
TYPE_PERSONAL_NUMBER = 7
TYPE_PAGER = 8
# A phone number is of type UNKNOWN when it does not fit any of the known
# patterns for a specific country.
TYPE_UNKNOWN = 9

# Types of phone number matches. See detailed description beside the
# is_number_match() method.
MATCH_TYPE_NO_MATCH = 0
MATCH_TYPE_SHORT_NSN_MATCH = 1
MATCH_TYPE_NSN_MATCH = 2
MATCH_TYPE_EXACT_MATCH = 3

# Possible outcomes when testing if a PhoneNumber is possible.
VALIDATION_RESULT_IS_POSSIBLE = 0
VALIDATION_RESULT_INVALID_COUNTRY_CODE = 1 
VALIDATION_RESULT_TOO_SHORT = 2
VALIDATION_RESULT_TOO_LONG = 3

# Init stuff from Java version getInstance()
supported_countries = []
for region_codes in metadata_gen.country_code_to_region_code_map.values():
    supported_countries.extend(region_codes)
nanpa_countries = \
    metadata_gen.country_code_to_region_code_map.get(_NANPA_COUNTRY_CODE)


def _load_metadata_for_region_from_file(region_code):
    source = open(_file_prefix + "_" + region_code, "rb")
    metadata_collection = phonemetadata_pb2.PhoneMetadataCollection()
    metadata_collection.ParseFromString(source.read())
    for metadata in metadata_collection.metadata:
        _country_to_metadata_map[region_code] = metadata

def extract_possible_number(number):
    """Attempts to extract a possible number from the string passed in.
    
    This currently strips all leading characters that could not be used to
    start a phone number. Characters that can be used to start a phone number
    are defined in the VALID_START_CHAR_PATTERN. If none of these characters
    are found in the number passed in, an empty string is returned. This
    function also attempts to strip off any alternative extensions or endings
    if two or more are present, such as in the case of: (530) 583-6985
    x302/x2303. The second extension here makes this actually two phone
    numbers, (530) 583-6985 x302 and (530) 583-6985 x2303. We remove the second
    extension so that the first number is parsed correctly.  
    
    Args:
        number the string that might contain a phone number.
    Returns:
        the number, stripped of any non-phone-number prefix (such as
        'Tel:' or an empty string if no character used to start phone numbers
        (such as + or any digit) is found in the number.
    """
    match = VALID_START_CHAR_PATTERN.search(number)
    if match:
        number = number[match.start(0):]
        # Remove trailing non-alpha non-numerical characters.
        number =_UNWANTED_END_CHAR_PATTERN.sub(u"", number)
        # Check for extra numbers at the end.
        match = _SECOND_NUMBER_START_PATTERN.search(number)
        if  match:
            number = number[0:match.start(0)]
    else:
        number = ""
    return number


def is_viable_phone_number(number):
    """Checks to see if the string of characters could possibly be a phone 
    number at all.
    
    At the moment, checks to see that the string begins with at least 3 digits,
    ignoring any punctuation commonly found in phone numbers. This method does
    not require the number to be normalized in advance - but does assume that
    leading non-number symbols have been removed, such as by the method
    extract_possible_number.
    
    Args:
        number string to be checked for viability as a phone number.
    Returns:
        True if the number could be a phone number of some sort, otherwise 
        False.
    """
    if len(number) < _MIN_LENGTH_FOR_NSN:
        return False
    return bool(_VALID_PHONE_NUMBER_PATTERN.match(number))


def normalize(number):
    """Normalizes a string of characters representing a phone number.
    
    This performs the following conversions:
        - Wide-ascii digits are converted to normal ASCII (European) digits.
        - Letters are converted to their numeric representation on a 
          telephone keypad. The keypad used here is the one defined in ITU
          Recommendation E.161. This is only done if there are 3 or more 
          letters in the number, to lessen the risk that such letters are 
          typos - otherwise alpha characters are stripped.
        - Punctuation is stripped.
        - Arabic-Indic numerals are converted to European numerals.

    Args:
        number a string of characters representing a phone number.
    Returns:
        the normalized string version of the phone number.
    """
    if _VALID_ALPHA_PHONE_PATTERN.match(number):
        return _normalize_helper(number, _ALL_NORMALIZATION_MAPPINGS, True)
    else:
        return _normalize_helper(number, DIGIT_MAPPINGS, True)


def normalize_string_buffer(number):
    """Normalizes a string of characters representing a phone number. 
    This is a wrapper for normalize(String number) but does in-place 
    normalization of the string buffer provided.
    
    Args:
        number a StringIO instance of characters representing a phone number.
    """
    normalized_number = normalize(number.to_string())
    number.clear()
    number.append(normalized_number)


def normalize_digits_only(number):
    """Normalizes a string of characters representing a phone number.
    This converts wide-ascii and arabic-indic numerals to European numerals,
    and strips punctuation and alpha characters.
    
    Args:
        number a string of characters representing a phone number.
    Returns:
        the normalized string version of the phone number.
    """
    return _normalize_helper(number, DIGIT_MAPPINGS, True)


def convert_alpha_characters_in_number(number):
    """Converts all alpha characters in a number to their respective digits 
    on a keypad, but retains existing formatting. Also converts wide-ascii 
    digits to normal ascii digits, and converts Arabic-Indic numerals to 
    European numerals.
    
    Args:
        number a string of characters representing a phone number.
    Returns:
        the normalized string version of the phone number.
    """
    return _normalize_helper(number, _ALL_NORMALIZATION_MAPPINGS, False)


def get_length_of_geographical_area_code(number):
    """Gets the length of the geographical area code from the national_number
    field of the Phone_number object passed in, so that clients could use it to
    split a national significant number into geographical area code and
    subscriber number.
    
    It works in such a way that the resultant subscriber number should be
    diallable, at least on some devices. An example of how this could be used:
    
    number = parse('16502530000', 'US')
    national_significant_number = get_national_significant_number(number)
    
    area_code_length = phone_util.get_length_of_geographical_area_code(number)
    if area_code_length > 0:
        area_code = national_significant_number[:area_code_length]
        subscriber_number = national_significant_number[area_code_length:]
    else:
        area_code = ""
        subscriber_number = national_significant_number
    
    N.B.: area code is a very ambiguous concept, so the I18N team generally
    recommends against using it for most purposes, but recommends using the
    more general national_number instead. Read the following carefully before
    deciding to use this method:

     - geographical area codes change over time, and this method honors those
       changes therefore, it doesn't guarantee the stability of the result it
       produces.
     - subscriber numbers may not be diallable from all devices (notably 
       mobile devices, which typically requires the full national_number to 
       be dialled in most countries).
     - most non-geographical numbers have no area codes.
     - some geographical numbers have no area codes.
    
    Args:
        number the PhoneNumber object for which clients want to know the 
        length of the area code in the national_number field.
    Returns:
        the length of area code of the Phone_number object passed in.
    """
    if not number:
        return 0
    region_code = get_region_code_for_number(number)
    if not _is_valid_region_code(region_code):
        return 0
    metadata = get_metadata_for_region(region_code)
    if not metadata.has_national_prefix():
        return 0
    type_ = _get_number_type_helper(
        get_national_significant_number(number), metadata)
    # Most numbers other than the two types below have to be dialled in full.
    if (type_ != TYPE_FIXED_LINE and
        type_ != TYPE_FIXED_LINE_OR_MOBILE):
        return 0
    return get_length_of_national_destination_code(number)



def get_length_of_national_destination_code(number):
    """Gets the length of the national destination code (NDC) from the
    Phone_number object passed in, so that clients could use it to split a
    national significant number into NDC and subscriber number. The NDC of a
    phone number is normally the first group of digit(s) right after the
    country code when the number is formatted in the international format, if
    there is a subscriber number part that follows. An example of how this
    could be used:
    
    number = parse('18002530000', 'US')
    national_significant_number = get_national_significant_number(number)
    
    national_destination_code_length =  \
            get_length_of_national_destination_code(number)
    if national_destination_code_length > 0:
        national_destination_code = \
                national_significant_number[:national_destination_code_length]
        subscriber_number = \
                national_significant_number[national_destination_code_length:]
    else:
        national_destination_code = ""
        subscriber_number = national_significant_number
    
    Refer to the unittests to see the difference between this function and
    get_length_of_geographical_area_code().

    Args:
        number the PhoneNumber object for which clients want to know the 
        length of the NDC.
    Returns:
        the length of NDC of the PhoneNumber object passed in.
    """
    if number.has_extension():
        # We don't want to alter the proto given to us, but we don't want to
        # include the extension when we format it, so we copy it and clear the
        # extension here.
        copied_proto = phonenumber_pb2.PhoneNumber()
        copied_proto.merge_from(number)
        copied_proto.clear_extension()
    else:
        copied_proto = number

    national_significant_number = format(copied_proto, FORMAT_INTERNATIONAL)
    number_groups = _NON_DIGITS_PATTERN.split(national_significant_number)
    
    # The pattern will start with '+COUNTRY_CODE ' so the first group will always
    # be the empty string (before the + symbol) and the second group will be the
    # country code. The third group will be area code if it's not the last group.
    if len(number_groups) <= 3:
        return 0
    
    if (get_region_code_for_number(number) == "AR" and
        get_number_type(number) == TYPE_MOBILE):
        # Argentinian mobile numbers, when formatted in the international format,
        # are in the form of +54 9 NDC XXXX.... As a result, we take the length of
        # the third group (NDC) and add 1 for the digit 9, which also forms part of
        # the national significant number.
        #
        # TODO: Investigate the possibility of better modeling the metadata to make
        # it easier to obtain the NDC.
        return len(number_groups[2]) + 1
    
    return len(number_groups[1])


def _normalize_helper(number, normalization_replacements, remove_non_matches):
    """Normalizes a string of characters representing a phone number by
    replacing all characters found in the accompanying map with the values
    therein, and stripping all other characters if remove_non_matches is true.
 
    Args:
            number a string of characters representing a phone number.
            normalization_replacements a mapping of characters to what they 
                    should be replaced by in the normalized version of the phone 
                    number.
            remove_non_matches indicates whether characters that are not able 
            to be replaced should be stripped from the number. If this is false,
            they will be left unchanged in the number.
    Returns:
            the normalized string version of the phone number.
    """
    normalized_number = []
    for character in number:
        new_digit = normalization_replacements.get(character.upper())
        if new_digit is not None:
                normalized_number.append(new_digit)
        elif not remove_non_matches:
                normalized_number.append(character)
        # If neither of the above are true, we remove this character.
    return "".join(normalized_number)


def _is_valid_region_code(region_code):
    """Helper function to check region code is not unknown or null.
    
    Args:
        region_code the ISO 3166-1 two-letter country code that denotes the 
        country/region that we want to get the country code for.
    Returns:
        True if region code is valid.
    """
    return region_code in supported_countries


def format(number, number_format):
    """Formats a phone number in the specified format using default rules.
    
    Note that this does not promise to produce a phone number that the user can
    dial from where they are - although we do format in either 'national' or
    'international' format depending on what the client asks for, we do not
    currently support a more abbreviated format, such as for users in the same
    "area" who could potentially dial the number without area code. Note that
    if the phone number has a country code of 0 or an otherwise invalid country
    code, we cannot work out which formatting rules to apply so we return the
    national significant number with no formatting applied.
   
    Params:
        number the phone number to be formatted.
        number_format the format the phone number should be formatted into.
    Returns:
        the formatted phone number.
    """
    country_code = number.get_country_code_or_default()
    national_significant_number = get_national_significant_number(number)
    if number_format == FORMAT_E164:
        # Early exit for E164 case since no formatting of the national 
        # number needs to be applied. Extensions are not formatted.
        return _format_number_by_format(
                country_code, FORMAT_E164, national_significant_number, "")
    
    # Note get_region_code_for_country_code() is used because formatting
    # information for countries which share a country code is contained by only
    # one country for performance reasons. For example, for NANPA countries it
    # will be contained in the metadata for US.
    region_code = get_region_code_for_country_code(country_code)
    if not _is_valid_region_code(region_code):
        return national_significant_number
    
    formatted_extension = _maybe_get_formatted_extension(number, region_code)
    formatted_national_number = _format_national_number(
            national_significant_number, region_code, number_format)
    return _format_number_by_format(country_code, number_format, 
            formatted_national_number, formatted_extension)


def format_by_pattern(number, number_format, user_defined_formats):
    """Formats a phone number in the specified format using client-defined
    formatting rules. 
    
    Note that if the phone number has a country code of zero or an otherwise
    invalid country code, we cannot work out things like whether there should
    be a national prefix applied, or how to format extensions, so we return the
    national significant number with no formatting applied.
    
    Args:
        number the phone number to be formatted.
        number_format the format the phone number should be formatted into.
        user_defined_formats formatting rules specified by clients.
    Returns:
        the formatted phone number.
    """
    country_code = number.get_country_code_or_default()
    national_significant_number = get_national_significant_number(number)
    
    # Note get_region_code_for_country_code() is used because formatting
    # information for countries which share a country code is contained by only
    # one country for performance reasons. For example, for NANPA countries it
    # will be contained in the metadata for US.
    region_code = get_region_code_for_country_code(country_code)
    if not _is_valid_region_code(region_code):
        return national_significant_number
    
    user_defined_formats_copy = []
    for num_format in user_defined_formats:
        national_prefix_formatting_rule = \
                num_format.get_national_prefix_formatting_rule_or_default()
        if len(national_prefix_formatting_rule) > 0:
    
            # Before we do a replacement of the national prefix pattern $NP
            # with the national prefix, we need to copy the rule so that
            # subsequent replacements for different numbers have the
            # appropriate national prefix.
            num_format_copy = phonemetadata_pb2.NumberFormat()
            num_format_copy.merge_from(num_format)
            national_prefix = \
        get_metadata_for_region(region_code).get_national_prefix_or_default()
            if len(national_prefix) > 0:
                # Replace $NP with national prefix and $FG with the first
                # group ($1).
                national_prefix_formatting_rule = _NP_PATTERN.sub(
                        national_prefix, national_prefix_formatting_rule)
                national_prefix_formatting_rule = _FG_PATTERN.sub(
                        "$1", national_prefix_formatting_rule)
                num_format_copy.set_national_prefix_formatting_rule(
                        national_prefix_formatting_rule)
            else:
                # We don't want to have a rule for how to format the national
                # prefix if there isn't one.
                num_format_copy.clear_national_prefix_formatting_rule()
            
            user_defined_formats_copy.append(num_format_copy)
        else:
            # Otherwise, we just add the original rule to the modified list of
            # formats.
            user_defined_formats_copy.append(num_format)

    formatted_extension = _maybe_get_formatted_extension(number, region_code)
    formatted_national_number = _format_according_to_formats(
            national_significant_number, user_defined_formats_copy, 
            number_format)
    return _format_number_by_format(country_code, number_format, 
            formatted_national_number, formatted_extension)


def format_national_number_with_carrier_code(number, carrier_code):
    country_code = number.get_country_code_or_default()
    national_significant_number = get_national_significant_number(number)
    # Note get_region_code_for_country_code() is used because formatting information
    # for countries which share a country code is contained by only one country
    # for performance reasons. For example, for NANPA countries it will be
    # contained in the metadata for US.
    region_code = get_region_code_for_country_code(country_code)
    if not _is_valid_region_code(region_code):
        return national_significant_number

    formatted_extension = _maybe_get_formatted_extension(number, region_code)
    formatted_national_number = _format_national_number(
            national_significant_number, region_code, FORMAT_NATIONAL, 
            carrier_code)
    return _format_number_by_format(country_code, FORMAT_NATIONAL,
            formatted_national_number, formatted_extension)



def format_out_of_country_calling_number(number, country_calling_from):
    """Formats a phone number for out-of-country dialing purpose. 
    
    If no country_calling_from is supplied, we format the number in its
    INTERNATIONAL format. If the country_calling_from is the same as the
    country where the number is from, then NATIONAL formatting will be applied.
    
    If the number itself has a country code of zero or an otherwise invalid
    country code, then we return the number with no formatting applied.
    
    Note this function takes care of the case for calling inside of NANPA and
    between Russia and Kazakhstan (who share the same country code). In those
    cases, no international prefix is used. For countries which have multiple
    international prefixes, the number in its INTERNATIONAL format will be
    returned instead.
   
    Args:
        number the phone number to be formatted.
        country_calling_from the ISO 3166-1 two-letter country code that 
            denotes the foreign country where the call is being placed.
    Returns:
        the formatted phone number.
    """
    if not _is_valid_region_code(country_calling_from):
        return format(number, FORMAT_INTERNATIONAL)
    country_code = number.get_country_code_or_default()
    region_code = get_region_code_for_country_code(country_code)
    national_significant_number = get_national_significant_number(number)
    if not _is_valid_region_code(region_code):
        return national_significant_number
    
    if country_code == _NANPA_COUNTRY_CODE:
        if is_nanpa_country(country_calling_from):
            # For NANPA countries, return the national format for these
            # countries but prefix it with the country code.
            return country_code + " "  + format(number, FORMAT_NATIONAL)
        
    elif country_code == get_country_code_for_region(country_calling_from):
        # For countries that share a country calling code, the country code
        # need not be dialled. This also applies when dialling within a
        # country, so this if clause covers both these cases. Technically this
        # is the case for dialling from la Reunion to other overseas
        # departments of France (French Guiana, Martinique, Guadeloupe), but
        # not vice versa - so we don't cover this edge case for now and for
        # those cases return the version including country code. Details here:
        # http:#www.petitfute.com/voyage/225-info-pratiques-reunion
        return format(number, FORMAT_NATIONAL)
    
    formatted_national_number = _format_national_number(
            national_significant_number, region_code, FORMAT_INTERNATIONAL)
    metadata = get_metadata_for_region(country_calling_from)
    international_prefix = metadata.get_international_prefix_or_default()
    formatted_extension = _maybe_get_formatted_extension(number, region_code)

    # For countries that have multiple international prefixes, the
    # international format of the number is returned, unless there is a
    # preferred international prefix.
    international_prefix_for_formatting = ""
    if _matches_entirely(_UNIQUE_INTERNATIONAL_PREFIX, international_prefix):
        international_prefix_for_formatting = international_prefix
    elif metadata.has_preferred_international_prefix():
        international_prefix_for_formatting = \
                metadata.get_preferred_international_prefix_or_default()
    
    if international_prefix_for_formatting != "":
        return "%s %s %s%s" % (international_prefix_for_formatting, 
                country_code, formatted_national_number, formatted_extension)
    else:
        return _format_number_by_format(country_code, FORMAT_INTERNATIONAL,
                formatted_national_number, formatted_extension)


def format_in_original_format(number, country_calling_from):
    """Formats a phone number using the original phone number format that the
    number is parsed from. 
    
    The original format is embedded in the country_code_source field of the
    PhoneNumber object passed in. If such information is missing, the number
    will be formatted into the NATIONAL format by default.
   
    Args:
        number the PhoneNumber that needs to be formatted in its original 
            number format.
        country_calling_from the country whose IDD needs to be prefixed if 
            the original number has one.
    Returns:
        the formatted phone number in its original number format.
    """
    if not number.has_country_code_source():
        return format(number, FORMAT_NATIONAL)
    country_code_source = number.get_country_code_source()
    if country_code_source == \
            phonenumber_pb2.PhoneNumber.FROM_NUMBER_WITH_PLUS_SIGN:
        return format(number, FORMAT_INTERNATIONAL)
    if country_code_source == \
            phonenumber_pb2.PhoneNumber.FROM_NUMBER_WITH_IDD:
        return format_out_of_country_calling_number(number, 
                country_calling_from)
    if country_code_source == \
            phonenumber_pb2.PhoneNumber.FROM_NUMBER_WITHOUT_PLUS_SIGN:
        return format(number, FORMAT_INTERNATIONAL)[1:]
    # Default phonenumber_pb2.PhoneNumber.FROM_DEFAULT_COUNTY
    return format(number, FORMAT_NATIONAL)


def get_national_significant_number(number):
    """Gets the national significant number of the a phone number.
    
    Note a national significant number doesn't contain a national prefix or any
    formatting.
   
    Args:
        number the PhoneNumber object for which the national significant 
        number is needed.
    Returns:
        the national significant number of the PhoneNumber object passed in.
    """
    # The leading zero in the national (significant) number of an Italian phone
    # number has a special meaning. Unlike the rest of the world, it indicates
    # the number is a landline number. There have been plans to migrate landline
    # numbers to start with the digit two since December 2000, but it has not yet
    # happened. See http:#en.wikipedia.org/wiki/%2B39 for more details.
    # Other countries such as Cote d'Ivoire and Gabon use this for their mobile
    # numbers.
    national_number = str(number.get_national_number())
    if (number.has_italian_leading_zero() and
        number.get_italian_leading_zero() and
        is_leading_zero_country(number.get_country_code_or_default())):
        return u"0" + national_number
    return national_number


def _format_number_by_format(country_code, number_format,
        formatted_national_number, formatted_extension):
    """
    A helper function that is used by format and format_by_pattern.
   
    Args:
        country_code the country calling code.
        number_format the format the phone number should be formatted into.
        formatted_national_number
        formatted_extension
    Returns:
        the formatted phone number.
    """
    if number_format == FORMAT_E164:
        return (PLUS_SIGN + country_code + formatted_national_number + 
                formatted_extension)
    if number_format == FORMAT_INTERNATIONAL:
        return (PLUS_SIGN + country_code + " " + formatted_national_number + 
                formatted_extension)
    # Default FORMAT_NATIONAL
    return formatted_national_number + formatted_extension


#/**
## Note in some countries, the national number can be written in two completely
## different ways depending on whether it forms part of the NATIONAL format or
## INTERNATIONAL format. The number_format parameter here is used to specify
## which format to use for those cases. If a carrier_code is specified, this will
## be inserted into the formatted string to replace $CC.
# *
## number a string of characters representing a phone number.
## region_code the ISO 3166-1 two-letter country code.
## number_format the format the
##           phone number should be formatted into.
## opt_carrier_code
## @return:string} the formatted phone number.
## @private
# */
#def _format_national_number
#        function(number, region_code, number_format, opt_carrier_code):
#
#    /** @type:i18n.phonenumbers.Phone_metadata} */
#    metadata = get_metadata_for_region(region_code)
#    /** @type:Array.<i18n.phonenumbers.Number_format>} */
#    intl_number_formats = metadata.intl_number_format_array()
#    # When the intl_number_formats exists, we use that to format national number
#    # for the INTERNATIONAL format instead of using the number_desc.number_formats.
#    /** @type:Array.<i18n.phonenumbers.Number_format>} */
#    available_formats =
#            (intl_number_formats.length == 0 ||
#                    number_format == FORMAT_NATIONAL) ?
#            metadata.number_format_array() : metadata.intl_number_format_array()
#    return _format_according_to_formats(number, available_formats, number_format,
#                                                                                opt_carrier_code)
#
#
#
#/**
## Note that carrier_code is optional - if NULL or an empty string, no carrier
## code replacement will take place. Carrier code replacement occurs before
## national prefix replacement.
# *
## national_number a string of characters representing a phone
##           number.
## available_formats the
##           available formats the phone number could be formatted into.
## number_format the format the
##           phone number should be formatted into.
## opt_carrier_code
## @return:string} the formatted phone number.
## @private
# */
#def _format_according_to_formats
#        function(national_number, available_formats, number_format, opt_carrier_code):
#
#    /** @type:i18n.phonenumbers.Number_format} */
#    num_format
#    /** @type:number} */
#    l = available_formats.length
#    for (var i = 0 i < l ++i):
#        num_format = available_formats[i]
#        /** @type:number} */
#        size = num_format.leading_digits_pattern_count()
#        if (size == 0 ||
#                # We always use the last leading_digits_pattern, as it is the most
#                # detailed.
#                national_number
#                        .search(num_format.get_leading_digits_pattern(size - 1)) == 0):
#            /** @type:Reg_exp} */
#            pattern_to_match = new Reg_exp(num_format.get_pattern())
#            /** @type:string} */
#            number_format_rule = num_format.get_format_or_default()
#            if (_matches_entirely(pattern_to_match,
#                                                                                                                         national_number)):
#                if opt_carrier_code != null && opt_carrier_code.length > 0:
#                    /** @type:string} */
#                    domestic_carrier_code_formatting_rule =
#                            num_format.get_domestic_carrier_code_formatting_rule_or_default()
#                    if domestic_carrier_code_formatting_rule.length > 0:
#                        # Replace the $CC in the formatting rule with the desired carrier
#                        # code.
#                        /** @type:string} */
#                        carrier_code_formatting_rule = domestic_carrier_code_formatting_rule
#                                .replace(_CC_PATTERN,
#                                                 opt_carrier_code)
#                        # Now replace the $FG in the formatting rule with the first group
#                        # and the carrier code combined in the appropriate way.
#                        number_format_rule = number_format_rule.replace(
#                                _FIRST_GROUP_PATTERN,
#                                carrier_code_formatting_rule)
#                    
#                
#                /** @type:string} */
#                national_prefix_formatting_rule =
#                        num_format.get_national_prefix_formatting_rule_or_default()
#                if (number_format == FORMAT_NATIONAL &&
#                        national_prefix_formatting_rule != null &&
#                        national_prefix_formatting_rule.length > 0):
#                    return national_number.replace(pattern_to_match, number_format_rule
#                            .replace(_FIRST_GROUP_PATTERN,
#                                             national_prefix_formatting_rule))
#                else:
#                    return national_number.replace(pattern_to_match, number_format_rule)
#                
#            
#        
#    
#
#    # If no pattern above is matched, we format the number as a whole.
#    return national_number
#
#
#
#/**
## Gets a valid number for the specified country.
# *
## region_code the ISO 3166-1 two-letter country code that
##           denotes the country for which an example number is needed.
## @return:i18n.phonenumbers.PhoneNumber} a valid fixed-line number for the
##           specified country. Returns null when the metadata does not contain such
##           information.
# */
#def get_example_number
#        function(region_code):
#
#    return get_example_number_for_type(region_code,
#            i18n.phonenumbers.PhoneNumber_type.FIXED_LINE)
#
#
#
#/**
## Gets a valid number, if any, for the specified country and number type.
# *
## region_code the ISO 3166-1 two-letter country code that
##           denotes the country for which an example number is needed.
## type the type of number that is
##           needed.
## @return:i18n.phonenumbers.PhoneNumber} a valid number for the specified
##           country and type. Returns null when the metadata does not contain such
##           information.
# */
#def get_example_number_for_type
#        function(region_code, type):
#
#    /** @type:i18n.phonenumbers.PhoneNumber_desc} */
#    desc = _get_number_desc_by_type(
#            get_metadata_for_region(region_code), type)
#    try:
#        if desc.has_example_number():
#            return parse(desc.get_example_number_or_default(), region_code)
#        
#    } catch (e):
#    
#    return null
#
#
#
#/**
## Gets the formatted extension of a phone number, if the phone number had an
## extension specified. If not, it returns an empty string.
# *
## number the PhoneNumber that might have
##           an extension.
## region_code the ISO 3166-1 two-letter country code.
## @return:string} the formatted extension if any.
## @private
# */
#def _maybe_get_formatted_extension
#        function(number, region_code):
#
#    if not number.has_extension():
#        return ''
#    else:
#        return _format_extension(number.get_extension_or_default(), region_code)
#    
#
#
#
#/**
## Formats the extension part of the phone number by prefixing it with the
## appropriate extension prefix. This will be the default extension prefix,
## unless overridden by a preferred extension prefix for this country.
# *
## extension_digits the extension digits.
## region_code the ISO 3166-1 two-letter country code.
## @return:string} the formatted extension.
## @private
# */
#def _format_extension
#        function(extension_digits, region_code):
#
#    /** @type:i18n.phonenumbers.Phone_metadata} */
#    metadata = get_metadata_for_region(region_code)
#    if metadata.has_preferred_extn_prefix():
#        return metadata.get_preferred_extn_prefix() + extension_digits
#    else:
#        return _DEFAULT_EXTN_PREFIX +
#                extension_digits
#    
#
#
#
#/**
## metadata
## type
## @return:i18n.phonenumbers.PhoneNumber_desc
## @private
# */
#def _get_number_desc_by_type
#        function(metadata, type):
#
#    switch (type):
#        case i18n.phonenumbers.PhoneNumber_type.PREMIUM_RATE:
#            return metadata.get_premium_rate()
#        case i18n.phonenumbers.PhoneNumber_type.TOLL_FREE:
#            return metadata.get_toll_free()
#        case i18n.phonenumbers.PhoneNumber_type.MOBILE:
#            return metadata.get_mobile()
#        case i18n.phonenumbers.PhoneNumber_type.FIXED_LINE:
#        case i18n.phonenumbers.PhoneNumber_type.FIXED_LINE_OR_MOBILE:
#            return metadata.get_fixed_line()
#        case i18n.phonenumbers.PhoneNumber_type.SHARED_COST:
#            return metadata.get_shared_cost()
#        case i18n.phonenumbers.PhoneNumber_type.VOIP:
#            return metadata.get_voip()
#        case i18n.phonenumbers.PhoneNumber_type.PERSONAL_NUMBER:
#            return metadata.get_personal_number()
#        case i18n.phonenumbers.PhoneNumber_type.PAGER:
#            return metadata.get_pager()
#        default:
#            return metadata.get_general_desc()
#    
#
#
#
#/**
## Gets the type of a phone number.
# *
## number the phone number that we want
##           to know the type.
## @return:i18n.phonenumbers.PhoneNumber_type} the type of the phone number.
# */
#def get_number_type
#        function(number):
#
#    /** @type:string} */
#    region_code = /** @type:string} */ (get_region_code_for_number(number))
#    if not _is_valid_region_code(region_code):
#        return i18n.phonenumbers.PhoneNumber_type.UNKNOWN
#    
#    /** @type:string} */
#    national_significant_number =
#            get_national_significant_number(number)
#    return _get_number_type_helper(national_significant_number,
#            get_metadata_for_region(region_code))
#
#
#
#/**
## national_number
## metadata
## @return:i18n.phonenumbers.PhoneNumber_type
## @private
# */
#def _get_number_type_helper
#        function(national_number, metadata):
#
#    /** @type:i18n.phonenumbers.PhoneNumber_desc} */
#    general_number_desc = metadata.get_general_desc()
#    if (not general_number_desc.has_national_number_pattern() ||
#            not _is_number_matching_desc(national_number, general_number_desc)):
#        return i18n.phonenumbers.PhoneNumber_type.UNKNOWN
#    
#
#    if _is_number_matching_desc(national_number, metadata.get_premium_rate()):
#        return i18n.phonenumbers.PhoneNumber_type.PREMIUM_RATE
#    
#    if _is_number_matching_desc(national_number, metadata.get_toll_free()):
#        return i18n.phonenumbers.PhoneNumber_type.TOLL_FREE
#    
#    if _is_number_matching_desc(national_number, metadata.get_shared_cost()):
#        return i18n.phonenumbers.PhoneNumber_type.SHARED_COST
#    
#    if _is_number_matching_desc(national_number, metadata.get_voip()):
#        return i18n.phonenumbers.PhoneNumber_type.VOIP
#    
#    if (_is_number_matching_desc(national_number,
#                                                                 metadata.get_personal_number())):
#        return i18n.phonenumbers.PhoneNumber_type.PERSONAL_NUMBER
#    
#    if (_is_number_matching_desc(national_number,
#                                                                 metadata.get_pager())):
#        return i18n.phonenumbers.PhoneNumber_type.PAGER
#    
#
#    /** @type:boolean} */
#    is_fixed_line = _is_number_matching_desc(national_number, metadata
#            .get_fixed_line())
#    if is_fixed_line:
#        if metadata.get_same_mobile_and_fixed_line_pattern():
#            return i18n.phonenumbers.PhoneNumber_type.FIXED_LINE_OR_MOBILE
#        } else if (_is_number_matching_desc(national_number,
#                                                                                    metadata.get_mobile())):
#            return i18n.phonenumbers.PhoneNumber_type.FIXED_LINE_OR_MOBILE
#        
#        return i18n.phonenumbers.PhoneNumber_type.FIXED_LINE
#    
#    # Otherwise, test to see if the number is mobile. Only do this if certain
#    # that the patterns for mobile and fixed line aren't the same.
#    if (not metadata.get_same_mobile_and_fixed_line_pattern() &&
#            _is_number_matching_desc(national_number, metadata.get_mobile())):
#        return i18n.phonenumbers.PhoneNumber_type.MOBILE
#    
#    return i18n.phonenumbers.PhoneNumber_type.UNKNOWN
#
#
#

def get_metadata_for_region(region_code):
    if not region_code:
        return
    region_code = region_code.upper()
    if not region_code in _country_to_metadata_map:
        _load_metadata_for_region_from_file(region_code)
#        metadata_serialized = \
#            metadata_gen.country_to_metadata.get(region_code)
#        if not metadata_serialized:
#            return
#        print metadata_serialized
#        metadata = phonemetadata_pb2.PhoneMetadata(metadata_serialized)
#        _country_to_metadata_map[region_code] = metadata
    return _country_to_metadata_map[region_code]


#/**
## national_number
## number_desc
## @return:boolean
## @private
# */
#def _is_number_matching_desc
#        function(national_number, number_desc):
#
#    return _matches_entirely(
#            number_desc.get_possible_number_pattern(), national_number) &&
#            _matches_entirely(
#                    number_desc.get_national_number_pattern(), national_number)
#
#
#
#/**
## Tests whether a phone number matches a valid pattern. Note this doesn't
## verify the number is actually in use, which is impossible to tell by just
## looking at a number it
# *
## number the phone number that we want
##           to validate.
## @return:boolean} a boolean that indicates whether the number is of a valid
##           pattern.
# */
#def is_valid_number function(number):
#    /** @type:string} */
#    region_code = /** @type:string} */ (get_region_code_for_number(number))
#    return _is_valid_region_code(region_code) &&
#            is_valid_number_for_region(number, region_code)
#
#
#
#/**
## Tests whether a phone number is valid for a certain region. Note this doesn't
## verify the number is actually in use, which is impossible to tell by just
## looking at a number it If the country code is not the same as the
## country code for the region, this immediately exits with false. After this,
## the specific number pattern rules for the region are examined. This is useful
## for determining for example whether a particular number is valid for Canada,
## rather than just a valid NANPA number.
# *
## number the phone number that we want
##           to validate.
## region_code the ISO 3166-1 two-letter country code that
##           denotes the region/country that we want to validate the phone number for.
## @return:boolean} a boolean that indicates whether the number is of a valid
##           pattern.
# */
#def is_valid_number_for_region
#        function(number, region_code):
#
#    if (number.get_country_code_or_default() !=
#            get_country_code_for_region(region_code)):
#        return false
#    
#    /** @type:i18n.phonenumbers.Phone_metadata} */
#    metadata = get_metadata_for_region(region_code)
#    /** @type:i18n.phonenumbers.PhoneNumber_desc} */
#    general_num_desc = metadata.get_general_desc()
#    /** @type:string} */
#    national_significant_number =
#            get_national_significant_number(number)
#
#    # For countries where we don't have metadata for PhoneNumber_desc, we treat
#    # any number passed in as a valid number if its national significant number
#    # is between the minimum and maximum lengths defined by ITU for a national
#    # significant number.
#    if not general_num_desc.has_national_number_pattern():
#        /** @type:number} */
#        number_length = national_significant_number.length
#        return number_length >
#                _MIN_LENGTH_FOR_NSN &&
#                number_length <= _MAX_LENGTH_FOR_NSN
#    
#    return _get_number_type_helper(national_significant_number, metadata) !=
#            i18n.phonenumbers.PhoneNumber_type.UNKNOWN
#
#
#


def get_region_code_for_number(number):
    """Returns the country/region where a phone number is from. 
    
    This could be used for geo-coding in the country/region level.

    Args:
        number the phone number whose origin we want to know.
    Returns:
        the country/region where the phone number is from, or None if no 
        country matches this calling code.
    """
    if not number: 
        return
    country_code = number.get_country_code_or_default()
    regions = metadata.country_code_to_region_code_map.get(country_code)
    if not regions: 
        return
    if len(regions) == 1:
        return regions[0]
    else:
        return _get_region_code_for_number_from_region_list(number, regions)
    

def _get_region_code_for_number_from_region_list(number, region_codes):
    national_number = str(number.get_national_number())
    for region_code in region_codes:
        # If leading_digits is present, use  Otherwise, do full validation.
        metadata = get_metadata_for_region(region_code)
        if metadata.has_leading_digits():
            if national_number.search(metadata.get_leading_digits()) == 0:
                return region_code
            
        elif _get_number_type_helper(national_number, metadata) != TYPE_UNKNOWN:
            return region_code
    return None


#/**
## Returns the region code that matches the specific country code. In the case
## of no region code being found, ZZ will be returned. In the case of multiple
## regions, the one designated in the metadata as the "main" country for this
## calling code will be returned.
# *
## country_code the country calling code.
## @return:string
# */
#def get_region_code_for_country_code
#        function(country_code):
#
#    /** @type:Array.<string>} */
#    region_codes =
#            i18n.phonenumbers.metadata.country_code_to_region_code_map[country_code]
#    return region_codes == None ? 'ZZ' : region_codes[0]
#
#
#
#/**
## Returns the country calling code for a specific region. For example, this
## would be 1 for the United States, and 64 for New Zealand.
# *
## region_code the ISO 3166-1 two-letter country code that
##           denotes the country/region that we want to get the country code for.
## @return:number} the country calling code for the country/region denoted by
##           region_code.
# */
#def get_country_code_for_region
#        function(region_code):
#
#    if not _is_valid_region_code(region_code):
#        return 0
#    
#    /** @type:i18n.phonenumbers.Phone_metadata} */
#    metadata = get_metadata_for_region(region_code)
#    if metadata == None:
#        return 0
#    
#    return metadata.get_country_code_or_default()
#
#
#
#/**
## Returns the national dialling prefix for a specific region. For example, this
## would be 1 for the United States, and 0 for New Zealand. Set strip_non_digits
## to true to strip symbols like "~" (which indicates a wait for a dialling
## tone) from the prefix returned. If no national prefix is present, we return
## None.
# *
## Warning: Do not use this method for do-your-own formatting - for some
## countries, the national dialling prefix is used only for certain types of
## numbers. Use the library's formatting functions to prefix the national prefix
## when required.
# *
## region_code the ISO 3166-1 two-letter country code that
##           denotes the country/region that we want to get the dialling prefix for.
## strip_non_digits true to strip non-digits from the national
##           dialling prefix.
## @return:?string} the dialling prefix for the country/region denoted by
##           region_code.
# */
#def get_ndd_prefix_for_region function(
#        region_code, strip_non_digits):
#    if not _is_valid_region_code(region_code):
#        return None
#    
#    /** @type:i18n.phonenumbers.Phone_metadata} */
#    metadata = get_metadata_for_region(region_code)
#    if metadata == None:
#        return None
#    
#    /** @type:string} */
#    national_prefix = metadata.get_national_prefix_or_default()
#    # If no national prefix was found, we return None.
#    if national_prefix.length == 0:
#        return None
#    
#    if strip_non_digits:
#        # Note: if any other non-numeric symbols are ever used in national
#        # prefixes, these would have to be removed here as well.
#        national_prefix = national_prefix.replace('~', '')
#    
#    return national_prefix
#
#
#
#/**
## Check if a country is one of the countries under the North American Numbering
## Plan Administration (NANPA).
# *
## region_code the ISO 3166-1 two-letter country code.
## @return:boolean} true if region_code is one of the countries under NANPA.
# */
#def is_nANPACountry
#        function(region_code):
#
#    return goog.array.contains(
#            i18n.phonenumbers.metadata.country_code_to_region_code_map[
#                    _NANPA_COUNTRY_CODE],
#            region_code.to_upper_case())
#
#
#
#/**
## Check whether country_code represents the country calling code from a country
## whose national significant number could contain a leading zero. An example of
## such a country is Italy.
# *
## country_code the country calling code.
## @return:boolean
# */
#is_leading_zero_country = function(country_code):
#    return country_code in
#            _LEADING_ZERO_COUNTRIES
#
#
#
#/**
## Convenience wrapper around is_possible_number_with_reason. Instead of returning
## the reason for failure, this method returns a boolean value.
# *
## number the number that needs to be
##           checked.
## @return:boolean} true if the number is possible.
# */
#def is_possible_number
#        function(number):
#
#    return is_possible_number_with_reason(number) ==
#            Validation_result.IS_POSSIBLE
#
#
#
#/**
## Check whether a phone number is a possible number. It provides a more lenient
## check than is_valid_number in the following sense:
# *
## 1. It only checks the length of phone numbers. In particular, it doesn't
## check starting digits of the number.
# *
## 2. It doesn't attempt to figure out the type of the number, but uses general
## rules which applies to all types of phone numbers in a country. Therefore, it
## is much faster than is_valid_number.
# *
## 3. For fixed line numbers, many countries have the concept of area code,
## which together with subscriber number constitute the national significant
## number. It is sometimes okay to dial the subscriber number only when dialing
## in the same area. This function will return true if the
## subscriber-number-only version is passed in. On the other hand, because
## is_valid_number validates using information on both starting digits (for fixed
## line numbers, that would most likely be area codes) and length (obviously
## includes the length of area codes for fixed line numbers), it will return
## false for the subscriber-number-only version.
# *
## number the number that needs to be
##           checked.
## @return:Validation_result} a
##           Validation_result object which indicates whether the number is possible.
# */
#def is_possible_number_with_reason
#        function(number):
#
#    /** @type:number} */
#    country_code = number.get_country_code_or_default()
#    # Note: For Russian Fed and NANPA numbers, we just use the rules from the
#    # default region (US or Russia) since the get_region_code_for_number will not
#    # work if the number is possible but not valid. This would need to be
#    # revisited if the possible number pattern ever differed between various
#    # countries within those plans.
#    /** @type:string} */
#    region_code = get_region_code_for_country_code(country_code)
#    if not _is_valid_region_code(region_code):
#        return Validation_result
#                .INVALID_COUNTRY_CODE
#    
#    /** @type:string} */
#    national_number =
#            get_national_significant_number(number)
#    /** @type:i18n.phonenumbers.PhoneNumber_desc} */
#    general_num_desc = get_metadata_for_region(region_code).get_general_desc()
#    # Handling case of numbers with no metadata.
#    if not general_num_desc.has_national_number_pattern():
#        /** @type:number} */
#        number_length = national_number.length
#        if number_length < _MIN_LENGTH_FOR_NSN:
#            return Validation_result.TOO_SHORT
#        } else if (number_length >
#                             _MAX_LENGTH_FOR_NSN):
#            return Validation_result.TOO_LONG
#        else:
#            return Validation_result.IS_POSSIBLE
#        
#    
#    /** @type:string} */
#    possible_number_pattern =
#            general_num_desc.get_possible_number_pattern_or_default()
#    /** @type:Array.<string> } */
#    matched_groups = national_number.match('^' + possible_number_pattern)
#    /** @type:string} */
#    first_group = matched_groups ? matched_groups[0] : ''
#    if first_group.length > 0:
#        return (first_group.length == national_number.length) ?
#                Validation_result.IS_POSSIBLE :
#                Validation_result.TOO_LONG
#    else:
#        return Validation_result.TOO_SHORT
#    
#
#
#
#/**
## Check whether a phone number is a possible number given a number in the form
## of a string, and the country where the number could be dialed from. It
## provides a more lenient check than is_valid_number. See
## is_possible_number(number) for details.
# *
## This method first parses the number, then invokes
## is_possible_number(PhoneNumber number) with the resultant PhoneNumber object.
# *
## number the number that needs to be checked, in the form of a
##           string.
## country_dialing_from the ISO 3166-1 two-letter country code
##           that denotes the country that we are expecting the number to be dialed
##           from. Note this is different from the country where the number belongs.
##           For example, the number +1 650 253 0000 is a number that belongs to US.
##           When written in this form, it could be dialed from any country. When it
##           is written as 00 1 650 253 0000, it could be dialed from any country
##           which uses an international dialling prefix of 00. When it is written as
##           650 253 0000, it could only be dialed from within the US, and when
##           written as 253 0000, it could only be dialed from within a smaller area
##           in the US (Mountain View, CA, to be more specific).
## @return:boolean} true if the number is possible.
# */
#def is_possible_number_string
#        function(number, country_dialing_from):
#
#    try:
#        return is_possible_number(parse(number, country_dialing_from))
#    } catch (e):
#        return false
#    
#
#
#
#/**
## Attempts to extract a valid number from a phone number that is too long to be
## valid, and resets the PhoneNumber object passed in to that valid version. If
## no valid number could be extracted, the PhoneNumber object passed in will not
## be modified.
## number a PhoneNumber object which
##           contains a number that is too long to be valid.
## @return:boolean} true if a valid phone number can be successfully extracted.
# */
#def truncate_too_long_number
#        function(number):
#
#    if is_valid_number(number):
#        return true
#    
#    /** @type:i18n.phonenumbers.PhoneNumber} */
#    number_copy = new i18n.phonenumbers.PhoneNumber()
#    number_copy.merge_from(number)
#    /** @type:number} */
#    national_number = number.get_national_number_or_default()
#    do:
#        national_number = Math.floor(national_number / 10)
#        number_copy.set_national_number(national_number)
#        if (national_number == 0 ||
#                is_possible_number_with_reason(number_copy) ==
#                        Validation_result.TOO_SHORT):
#            return false
#        
#    } while (not is_valid_number(number_copy))
#    number.set_national_number(national_number)
#    return true
#
#
#
#/**
## Extracts country code from full_number, returns it and places the remaining
## number in national_number. It assumes that the leading plus sign or IDD has
## already been removed. Returns 0 if full_number doesn't start with a valid
## country code, and leaves national_number unmodified.
# *
## full_number
## national_number
## @return:number
# */
#def extract_country_code
#        function(full_number, national_number):
#
#    /** @type:string} */
#    full_number_str = full_number.to_string()
#    /** @type:number} */
#    potential_country_code
#    /** @type:number} */
#    number_length = full_number_str.length
#    for (var i = 1 i <= 3 && i <= number_length ++i):
#        potential_country_code = parse_int(full_number_str.substring(0, i), 10)
#        if (potential_country_code in
#                i18n.phonenumbers.metadata.country_code_to_region_code_map):
#            national_number.append(full_number_str.substring(i))
#            return potential_country_code
#        
#    
#    return 0
#
#
#
#/**
## Tries to extract a country code from a number. This method will return zero
## if no country code is considered to be present. Country codes are extracted
## in the following ways:
##    - by stripping the international dialing prefix of the country the person is
## dialing from, if this is present in the number, and looking at the next
## digits
##    - by stripping the '+' sign if present and then looking at the next digits
##    - by comparing the start of the number and the country code of the default
## region. If the number is not considered possible for the numbering plan of
## the default region initially, but starts with the country code of this
## region, validation will be reattempted after stripping this country code. If
## this number is considered a possible number, then the first digits will be
## considered the country code and removed as such.
# *
## It will throw a i18n.phonenumbers.Error if the number starts with a '+' but
## the country code supplied after this does not match that of any known
## country.
# *
## number non-normalized telephone number that we wish to
##           extract a country code from - may begin with '+'.
## default_region_metadata metadata
##           about the region this number may be from.
## national_number a string buffer to store
##           the national significant number in, in the case that a country code was
##           extracted. The number is appended to any existing contents. If no country
##           code was extracted, this will be left unchanged.
## store_country_code_source true if the country_code_source field
##           of phone_number should be populated.
## phone_number the PhoneNumber object
##           that needs to be populated with country code and country code source.
##           Note the country code is always populated, whereas country code source is
##           only populated when keep_country_code_source is true.
## @return:number} the country code extracted or 0 if none could be extracted.
## @throws:i18n.phonenumbers.Error
# */
#def maybe_extract_country_code
#        function(number, default_region_metadata, national_number,
#                         store_country_code_source, phone_number):
#
#    if number.length == 0:
#        return 0
#    
#    /** @type:!goog.string.String_buffer} */
#    full_number = new goog.string.String_buffer(number)
#    # Set the default prefix to be something that will never match.
#    /** @type:?string} */
#    possible_country_idd_prefix
#    if default_region_metadata != None:
#        possible_country_idd_prefix = default_region_metadata.get_international_prefix()
#    
#    if possible_country_idd_prefix == None:
#        possible_country_idd_prefix = 'Non_match'
#    
#
#    /** @type:i18n.phonenumbers.PhoneNumber.Country_code_source} */
#    country_code_source = maybe_strip_international_prefix_and_normalize(
#            full_number, possible_country_idd_prefix)
#    if store_country_code_source:
#        phone_number.set_country_code_source(country_code_source)
#    
#    if (country_code_source !=
#            i18n.phonenumbers.PhoneNumber.Country_code_source.FROM_DEFAULT_COUNTRY):
#        if (full_number.get_length() <
#                _MIN_LENGTH_FOR_NSN):
#            throw i18n.phonenumbers.Error.TOO_SHORT_AFTER_IDD
#        
#        /** @type:number} */
#        potential_country_code = extract_country_code(full_number,
#                                                                                                             national_number)
#        if potential_country_code != 0:
#            phone_number.set_country_code(potential_country_code)
#            return potential_country_code
#        
#
#        # If this fails, they must be using a strange country code that we don't
#        # recognize, or that doesn't exist.
#        throw i18n.phonenumbers.Error.INVALID_COUNTRY_CODE
#    } else if default_region_metadata != None:
#        # Check to see if the number is valid for the default region already. If
#        # not, we check to see if the country code for the default region is
#        # present at the start of the number.
#        /** @type:i18n.phonenumbers.PhoneNumber_desc} */
#        general_desc = default_region_metadata.get_general_desc()
#        /** @type:Reg_exp} */
#        valid_number_pattern = new Reg_exp(general_desc.get_national_number_pattern())
#        if (not _matches_entirely(
#                valid_number_pattern, full_number.to_string())):
#            /** @type:number} */
#            default_country_code = default_region_metadata.get_country_code_or_default()
#            /** @type:string} */
#            default_country_code_string = '' + default_country_code
#            /** @type:string} */
#            normalized_number = full_number.to_string()
#            if goog.string.starts_with(normalized_number, default_country_code_string):
#                # If so, strip this, and see if the resultant number is valid.
#                /** @type:!goog.string.String_buffer} */
#                potential_national_number = new goog.string.String_buffer(
#                        normalized_number.substring(default_country_code_string.length))
#                maybe_strip_national_prefix(potential_national_number,
#                        default_region_metadata.get_national_prefix_for_parsing(),
#                        default_region_metadata.get_national_prefix_transform_rule(),
#                        valid_number_pattern)
#                /** @type:string} */
#                potential_national_number_str = potential_national_number.to_string()
#                /** @type:Array.<string> } */
#                matched_groups = potential_national_number_str.match(
#                        '^' + general_desc.get_possible_number_pattern())
#                /** @type:number} */
#                possible_number_matched_length = matched_groups &&
#                        matched_groups[0] != None && matched_groups[0].length || 0
#                # If the resultant number is either valid, or still too long even with
#                # the country code stripped, we consider this a better result and keep
#                # the potential national number.
#                if (_matches_entirely(
#                        valid_number_pattern, potential_national_number_str) ||
#                        possible_number_matched_length > 0 &&
#                        possible_number_matched_length != potential_national_number_str.length):
#                    national_number.append(potential_national_number_str)
#                    if store_country_code_source:
#                        phone_number.set_country_code_source(
#                                i18n.phonenumbers.PhoneNumber.Country_code_source
#                                        .FROM_NUMBER_WITHOUT_PLUS_SIGN)
#                    
#                    phone_number.set_country_code(default_country_code)
#                    return default_country_code
#                
#            
#        
#    
#    # No country code present.
#    phone_number.set_country_code(0)
#    return 0
#
#
#
#/**
## Strips the IDD from the start of the number if present. Helper function used
## by maybe_strip_international_prefix_and_normalize.
# *
## idd_pattern the regular expression for the international
##           prefix.
## number the phone number that we wish to
##           strip any international dialing prefix from.
## @return:boolean} true if an international prefix was present.
## @private
# */
#def _parse_prefix_as_idd
#        function(idd_pattern, number):
#
#    /** @type:string} */
#    number_str = number.to_string()
#    if number_str.search(idd_pattern) == 0:
#        /** @type:number} */
#        match_end = number_str.match(idd_pattern)[0].length
#        /** @type:Array.<string> } */
#        matched_groups = number_str.substring(match_end).match(
#                _CAPTURING_DIGIT_PATTERN)
#        if (matched_groups && matched_groups[1] != None &&
#                matched_groups[1].length > 0):
#            /** @type:string} */
#            normalized_group = _normalize_helper(
#                    matched_groups[1], DIGIT_MAPPINGS,
#                    true)
#            if normalized_group == '0':
#                return false
#            
#        
#        number.clear()
#        number.append(number_str.substring(match_end))
#        return true
#    
#    return false
#
#
#
#/**
## Strips any international prefix (such as +, 00, 011) present in the number
## provided, normalizes the resulting number, and indicates if an international
## prefix was present.
# *
## number the non-normalized telephone number
##           that we wish to strip any international dialing prefix from.
## possible_idd_prefix the international direct dialing prefix
##           from the country we think this number may be dialed in.
## @return:i18n.phonenumbers.PhoneNumber.Country_code_source} the corresponding
##           Country_code_source if an international dialing prefix could be removed
##           from the number, otherwise Country_code_source.FROM_DEFAULT_COUNTRY if
##           the number did not seem to be in international format.
# */
#prototype.
#        maybe_strip_international_prefix_and_normalize = function(number,
#                                                                                                                 possible_idd_prefix):
#    /** @type:string} */
#    number_str = number.to_string()
#    if number_str.length == 0:
#        return i18n.phonenumbers.PhoneNumber.Country_code_source.FROM_DEFAULT_COUNTRY
#    
#    # Check to see if the number begins with one or more plus signs.
#    if _PLUS_CHARS_PATTERN.test(number_str):
#        number_str = number_str.replace(
#                _PLUS_CHARS_PATTERN, '')
#        # Can now normalize the rest of the number since we've consumed the "+"
#        # sign at the start.
#        number.clear()
#        number.append(normalize(number_str))
#        return i18n.phonenumbers.PhoneNumber.Country_code_source
#                .FROM_NUMBER_WITH_PLUS_SIGN
#    
#    # Attempt to parse the first digits as an international prefix.
#    /** @type:Reg_exp} */
#    idd_pattern = new Reg_exp(possible_idd_prefix)
#    if _parse_prefix_as_idd(idd_pattern, number):
#        _normalize_sB(number)
#        return i18n.phonenumbers.PhoneNumber.Country_code_source.FROM_NUMBER_WITH_IDD
#    
#    # If still not found, then try and normalize the number and then try again.
#    # This shouldn't be done before, since non-numeric characters (+ and ~) may
#    # legally be in the international prefix.
#    _normalize_sB(number)
#    return _parse_prefix_as_idd(idd_pattern, number) ?
#            i18n.phonenumbers.PhoneNumber.Country_code_source.FROM_NUMBER_WITH_IDD :
#            i18n.phonenumbers.PhoneNumber.Country_code_source.FROM_DEFAULT_COUNTRY
#
#
#
#/**
## Strips any national prefix (such as 0, 1) present in the number provided.
# *
## number the normalized telephone number
##           that we wish to strip any national dialing prefix from.
## possible_national_prefix a regex that represents the national
##           direct dialing prefix from the country we think this number may be dialed
##           in.
## transform_rule the string that specifies how number should be
##           transformed according to the regex specified in possible_national_prefix.
## national_number_rule a regular expression that specifies what a
##           valid phonenumber from this region should look like after any national
##           prefix was stripped or transformed.
# */
#def maybe_strip_national_prefix
#        function(number, possible_national_prefix, transform_rule,
#                         national_number_rule):
#
#    /** @type:string} */
#    number_str = number.to_string()
#    /** @type:number} */
#    number_length = number_str.length
#    if (number_length == 0 || possible_national_prefix == None ||
#            possible_national_prefix.length == 0):
#        # Early return for numbers of zero length.
#        return
#    
#    # Attempt to parse the first digits as a national prefix.
#    /** @type:Reg_exp} */
#    re = new Reg_exp('^' + possible_national_prefix)
#    /** @type:Array.<string>} */
#    m = re.exec(number_str)
#    if m:
#        /** @type:string} */
#        transformed_number
#        # m[1] == None implies nothing was captured by the capturing groups in
#        # possible_national_prefix therefore, no transformation is necessary, and
#        # we just remove the national prefix.
#        if (transform_rule == None || transform_rule.length == 0 || m[1] == None ||
#                m[1].length == 0):
#            transformed_number = number_str.substring(m[0].length)
#        else:
#            transformed_number = number_str.replace(re, transform_rule)
#        
#        # Check that the resultant number is viable. If not, return.
#        if (not _matches_entirely(national_number_rule,
#                transformed_number)):
#            return
#        
#        number.clear()
#        number.append(transformed_number)
#    
#
#
#
#/**
## Strips any extension (as in, the part of the number dialled after the call is
## connected, usually indicated with extn, ext, x or similar) from the end of
## the number, and returns it.
# *
## number the non-normalized telephone number
##           that we wish to strip the extension from.
## @return:string} the phone extension.
# */
#def maybe_strip_extension
#        function(number):
#
#    /** @type:string} */
#    number_str = number.to_string()
#    /** @type:number} */
#    m_start =
#            number_str.search(_EXTN_PATTERN)
#    # If we find a potential extension, and the number preceding this is a viable
#    # number, we assume it is an extension.
#    if (m_start >= 0 && is_viable_phone_number(
#            number_str.substring(0, m_start))):
#        # The numbers are captured into groups in the regular expression.
#        /** @type:Array.<string>} */
#        matched_groups =
#                number_str.match(_EXTN_PATTERN)
#        /** @type:number} */
#        matched_groups_length = matched_groups.length
#        for (var i = 1 i < matched_groups_length ++i):
#            if matched_groups[i] != None && matched_groups[i].length > 0:
#                number.clear()
#                number.append(number_str.substring(0, m_start))
#                return matched_groups[i]
#            
#        
#    
#    return ''
#
#
#
#/**
## Checks to see that the region code used is valid, or if it is not valid, that
## the number to parse starts with a + symbol so that we can attempt to infer
## the country from the number.
## number_to_parse number that we are attempting to parse.
## default_country the ISO 3166-1 two-letter country code that
##           denotes the country that we are expecting the number to be from.
## @return:boolean} false if it cannot use the region provided and the region
##           cannot be inferred.
## @private
# */
#def _check_region_for_parsing function(
#        number_to_parse, default_country):
#    return _is_valid_region_code(default_country) ||
#            (number_to_parse != None && number_to_parse.length > 0 &&
#                    _PLUS_CHARS_PATTERN.test(
#                            number_to_parse))
#
#
#
#/**
## Parses a string and returns it in proto buffer format. This method will throw
## a i18n.phonenumbers.Error if the number is not considered to be a possible
## number. Note that validation of whether the number is actually a valid number
## for a particular country/region is not performed. This can be done separately
## with is_valid_number.
# *
## number_to_parse number that we are attempting to parse. This
##           can contain formatting such as +, ( and -, as well as a phone number
##           extension.
## default_country the ISO 3166-1 two-letter country code that
##           denotes the country that we are expecting the number to be from. This is
##           only used if the number being parsed is not written in international
##           format. The country code for the number in this case would be stored as
##           that of the default country supplied.    If the number is guaranteed to
##           start with a '+' followed by the country code, then 'ZZ' or None can be
##           supplied.
## @return:i18n.phonenumbers.PhoneNumber} a phone number proto buffer filled
##           with the parsed number.
## @throws:i18n.phonenumbers.Error} if the string is not considered to be a
##           viable phone number or if no default country was supplied and the number
##           is not in international format (does not start with +).
# */
#def parse function(number_to_parse,
#                                                                                                                         default_country):
#    return _parse_helper(number_to_parse, default_country, false, true)
#
#
#
#/**
## Parses a string and returns it in proto buffer format. This method differs
## from parse() in that it always populates the raw_input field of the protocol
## buffer with number_to_parse as well as the country_code_source field.
# *
## number_to_parse number that we are attempting to parse. This
##           can contain formatting such as +, ( and -, as well as a phone number
##           extension.
## default_country the ISO 3166-1 two-letter country code that
##           denotes the country that we are expecting the number to be from. This is
##           only used if the number being parsed is not written in international
##           format. The country code for the number in this case would be stored as
##           that of the default country supplied.
## @return:i18n.phonenumbers.PhoneNumber} a phone number proto buffer filled
##           with the parsed number.
## @throws:i18n.phonenumbers.Error} if the string is not considered to be a
##           viable phone number or if no default country was supplied and the number
##           is not in international format (does not start with +).
# */
#def parse_and_keep_raw_input
#        function(number_to_parse, default_country):
#
#    if not _is_valid_region_code(default_country):
#        if (number_to_parse.length > 0 && number_to_parse.char_at(0) !=
#                PLUS_SIGN):
#            throw i18n.phonenumbers.Error.INVALID_COUNTRY_CODE
#        
#    
#    return _parse_helper(number_to_parse, default_country, true, true)
#
#
#
#/**
## Parses a string and returns it in proto buffer format. This method is the
## same as the public parse() method, with the exception that it allows the
## default country to be None, for use by is_number_match().
# *
## number_to_parse number that we are attempting to parse. This
##           can contain formatting such as +, ( and -, as well as a phone number
##           extension.
## default_country the ISO 3166-1 two-letter country code that
##           denotes the country that we are expecting the number to be from. This is
##           only used if the number being parsed is not written in international
##           format. The country code for the number in this case would be stored as
##           that of the default country supplied.
## keep_raw_input whether to populate the raw_input field of the
##           phone_number with number_to_parse.
## check_region should be set to false if it is permitted for
##           the default country to be None or unknown ('ZZ').
## @return:i18n.phonenumbers.PhoneNumber} a phone number proto buffer filled
##           with the parsed number.
## @throws:i18n.phonenumbers.Error
## @private
# */
#def _parse_helper
#        function(number_to_parse, default_country, keep_raw_input, check_region):
#
#    if number_to_parse == None:
#        throw i18n.phonenumbers.Error.NOT_A_NUMBER
#    
#    # Extract a possible number from the string passed in (this strips leading
#    # characters that could not be the start of a phone number.)
#    /** @type:string} */
#    number =
#            extract_possible_number(number_to_parse)
#    if not is_viable_phone_number(number):
#        throw i18n.phonenumbers.Error.NOT_A_NUMBER
#    
#
#    # Check the country supplied is valid, or that the extracted number starts
#    # with some sort of + sign so the number's region can be determined.
#    if check_region && not _check_region_for_parsing(number, default_country):
#        throw i18n.phonenumbers.Error.INVALID_COUNTRY_CODE
#    
#
#    /** @type:i18n.phonenumbers.PhoneNumber} */
#    phone_number = new i18n.phonenumbers.PhoneNumber()
#    if keep_raw_input:
#        phone_number.set_raw_input(number_to_parse)
#    
#    /** @type:!goog.string.String_buffer} */
#    national_number = new goog.string.String_buffer(number)
#    # Attempt to parse extension first, since it doesn't require
#    # country-specific data and we want to have the non-normalised number here.
#    /** @type:string} */
#    extension = maybe_strip_extension(national_number)
#    if extension.length > 0:
#        phone_number.set_extension(extension)
#    
#
#    /** @type:i18n.phonenumbers.Phone_metadata} */
#    country_metadata = get_metadata_for_region(default_country)
#    # Check to see if the number is given in international format so we know
#    # whether this number is from the default country or not.
#    /** @type:!goog.string.String_buffer} */
#    normalized_national_number = new goog.string.String_buffer()
#    /** @type:number} */
#    country_code = maybe_extract_country_code(national_number.to_string(),
#            country_metadata, normalized_national_number, keep_raw_input, phone_number)
#    if country_code != 0:
#        /** @type:string} */
#        phone_number_region = get_region_code_for_country_code(country_code)
#        if phone_number_region != default_country:
#            country_metadata = get_metadata_for_region(phone_number_region)
#        
#    else:
#        # If no extracted country code, use the region supplied instead. The
#        # national number is just the normalized version of the number we were
#        # given to parse.
#        _normalize_sB(national_number)
#        normalized_national_number.append(national_number.to_string())
#        if default_country != None:
#            country_code = country_metadata.get_country_code_or_default()
#            phone_number.set_country_code(country_code)
#        } else if keep_raw_input:
#            phone_number.clear_country_code_source()
#        
#    
#    if (normalized_national_number.get_length() <
#            _MIN_LENGTH_FOR_NSN):
#        throw i18n.phonenumbers.Error.TOO_SHORT_NSN
#    
#
#    if country_metadata != None:
#        /** @type:Reg_exp} */
#        valid_number_pattern =
#                new Reg_exp(country_metadata.get_general_desc().get_national_number_pattern())
#        maybe_strip_national_prefix(normalized_national_number, country_metadata
#                .get_national_prefix_for_parsing(), country_metadata
#                .get_national_prefix_transform_rule(), valid_number_pattern)
#    
#    /** @type:string} */
#    normalized_national_number_str = normalized_national_number.to_string()
#    /** @type:number} */
#    length_of_national_number = normalized_national_number_str.length
#    if (length_of_national_number <
#            _MIN_LENGTH_FOR_NSN):
#        throw i18n.phonenumbers.Error.TOO_SHORT_NSN
#    
#    if (length_of_national_number >
#            _MAX_LENGTH_FOR_NSN):
#        throw i18n.phonenumbers.Error.TOO_LONG
#    
#    if (normalized_national_number_str.char_at(0) == '0' &&
#            is_leading_zero_country(country_code)):
#        phone_number.set_italian_leading_zero(true)
#    
#    phone_number.set_national_number(parse_int(normalized_national_number_str, 10))
#    return phone_number
#
#
#
#/**
## Takes two phone numbers and compares them for equality.
# *
## Returns EXACT_MATCH if the country code, NSN, presence of a leading zero for
## Italian numbers and any extension present are the same. Returns NSN_MATCH if
## either or both has no country specified, and the NSNs and extensions are the
## same. Returns SHORT_NSN_MATCH if either or both has no country specified, or
## the country specified is the same, and one NSN could be a shorter version of
## the other number. This includes the case where one has an extension
## specified, and the other does not. Returns NO_MATCH otherwise. For example,
## the numbers +1 345 657 1234 and 657 1234 are a SHORT_NSN_MATCH. The numbers
## +1 345 657 1234 and 345 657 are a NO_MATCH.
# *
## first_number_in first number to
##           compare. If it is a string it can contain formatting, and can have
##           country code specified with + at the start.
## second_number_in second number to
##           compare. If it is a string it can contain formatting, and can have
##           country code specified with + at the start.
## @return:Match_type} NO_MATCH,
##           SHORT_NSN_MATCH, NSN_MATCH or EXACT_MATCH depending on the level of
##           equality of the two numbers, described in the method definition.
## @throws:i18n.phonenumbers.Error} if either number is not considered to be
##           a viable phone number.
# */
#def is_number_match
#        function(first_number_in, second_number_in):
#
#    /** @type:i18n.phonenumbers.PhoneNumber} */
#    first_number
#    /** @type:i18n.phonenumbers.PhoneNumber} */
#    second_number
#    # If the input arguements are strings parse them to a proto buffer format.
#    # Else make copies of the phone numbers so that the numbers passed in are not
#    # edited.
#    if typeof first_number_in == 'string':
#        first_number = _parse_helper(first_number_in, None, false, false)
#    else:
#        first_number = new i18n.phonenumbers.PhoneNumber()
#        first_number.merge_from(first_number_in)
#    
#    if typeof second_number_in == 'string':
#        second_number = _parse_helper(second_number_in, None, false, false)
#    else:
#        second_number = new i18n.phonenumbers.PhoneNumber()
#        second_number.merge_from(second_number_in)
#    
#    # First clear raw_input and country_code_source field and any empty-string
#    # extensions so that
#    # we can use the PhoneNumber.exactly_same_as() method.
#    first_number.clear_raw_input()
#    first_number.clear_country_code_source()
#    second_number.clear_raw_input()
#    second_number.clear_country_code_source()
#    if first_number.has_extension() && first_number.get_extension().length == 0:
#        first_number.clear_extension()
#    
#    if second_number.has_extension() && second_number.get_extension().length == 0:
#        second_number.clear_extension()
#    
#
#    # Early exit if both had extensions and these are different.
#    if (first_number.has_extension() && second_number.has_extension() &&
#            first_number.get_extension() != second_number.get_extension()):
#        return Match_type.NO_MATCH
#    
#    /** @type:number} */
#    first_number_country_code = first_number.get_country_code_or_default()
#    /** @type:number} */
#    second_number_country_code = second_number.get_country_code_or_default()
#    # Both had country code specified.
#    if first_number_country_code != 0 && second_number_country_code != 0:
#        if first_number.exactly_same_as(second_number):
#            return Match_type.EXACT_MATCH
#        } else if (first_number_country_code == second_number_country_code &&
#                _is_national_number_suffix_of_the_other(first_number, second_number)):
#            # A SHORT_NSN_MATCH occurs if there is a difference because of the
#            # presence or absence of an 'Italian leading zero', the presence or
#            # absence of an extension, or one NSN being a shorter variant of the
#            # other.
#            return Match_type.SHORT_NSN_MATCH
#        
#        # This is not a match.
#        return Match_type.NO_MATCH
#    
#    # Checks cases where one or both country codes were not specified. To make
#    # equality checks easier, we first set the country codes to be equal.
#    first_number.set_country_code(0)
#    second_number.set_country_code(0)
#    # If all else was the same, then this is an NSN_MATCH.
#    if first_number.exactly_same_as(second_number):
#        return Match_type.NSN_MATCH
#    
#    if _is_national_number_suffix_of_the_other(first_number, second_number):
#        return Match_type.SHORT_NSN_MATCH
#    
#    return Match_type.NO_MATCH
#
#
#
#/**
## Returns true when one national number is the suffix of the other or both are
## the same.
# *
## first_number the first PhoneNumber
##           object.
## second_number the second PhoneNumber
##           object.
## @return:boolean} true if one PhoneNumber is the suffix of the other one.
## @private
# */
#def _is_national_number_suffix_of_the_other
#        function(first_number, second_number):
#
#    /** @type:string} */
#    first_number_national_number = '' + first_number.get_national_number()
#    /** @type:string} */
#    second_number_national_number = '' + second_number.get_national_number()
#    # Note that ends_with returns true if the numbers are equal.
#    return goog.string.ends_with(first_number_national_number,
#                                                            second_number_national_number) ||
#                 goog.string.ends_with(second_number_national_number,
#                                                            first_number_national_number)
#
#
#
#/**
## Check whether the entire input sequence can be matched against the regular
## expression.
# *
## regex the regular expression to match against.
## str the string to test.
## @return:boolean} true if str can be matched entirely against regex.
## @private
# */
#_matches_entirely = function(regex, str):
#    /** @type:Array.<string>} */
#    matched_groups = str.match(regex)
#    if matched_groups && matched_groups[0].length == str.length:
#        return true
#    
#    return false
#
#
#
#/**
## other
## @return:boolean
# */
#i18n.phonenumbers.PhoneNumber.def exactly_same_as function(other):
#    return other != None &&
#            get_country_code() == other.get_country_code() &&
#            get_national_number() == other.get_national_number() &&
#            get_extension() == other.get_extension() &&
#            get_italian_leading_zero() == other.get_italian_leading_zero() &&
#            get_raw_input() == other.get_raw_input() &&
#            get_country_code_source() == other.get_country_code_source()
#
#
#
#/**
## other
## @return:boolean
# */
#i18n.phonenumbers.PhoneNumber_desc.def exactly_same_as function(other):
#    return other != None &&
#            get_national_number_pattern() == other.get_national_number_pattern() &&
#            get_possible_number_pattern() == other.get_possible_number_pattern() &&
#            get_example_number() == other.get_example_number()
#
#
#
#/**
## other
## @return:i18n.phonenumbers.PhoneNumber
## @suppress:access_controls
# */
#i18n.phonenumbers.PhoneNumber.def merge_from function(other):
#    if other:
#        _values = goog.clone_object(other._values)
#    
#    return this
#
#
#
#/**
## other
## @return:i18n.phonenumbers.Number_format
## @suppress:access_controls
# */
#i18n.phonenumbers.Number_format.def merge_from function(other):
#    if other:
#        _values = goog.clone_object(other._values)
#    
#    return this

if __name__ == "__main__":
    print get_metadata_for_region("US")