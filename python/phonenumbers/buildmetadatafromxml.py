#!/usr/bin/env python

"""Library to build phone number metadata from the XML format.

Based on BuildMetadataFromXml.java.
"""

import logging
import re
import xml.etree.ElementTree

from phonenumbers import phonemetadata_pb2


_lite_build = False


def build_phone_metadata_collection(input_xml_file, lite_build):
    """Build the PhoneMetadataCollection from the input XML file."""
    global _lite_build
    _lite_build = lite_build
    tree = xml.etree.ElementTree.parse(input_xml_file)
    metadata_collection = phonemetadata_pb2.PhoneMetadataCollection()
    for territory in tree.getiterator("territory"):
        region_code = territory.attrib["id"]
        # Unlike Java version, use add() to create new PhoneMetadata instance
        # and pass it to _load_country_metadata(). This saves having to make
        # a copy of all metadata when calling extend(). See 'Repeated Message
        # Fields' on
        # http://code.google.com/apis/protocolbuffers/docs/reference/python-generated.html
        metadata = metadata_collection.metadata.add()
        _load_country_metadata(region_code, territory, metadata)
    return metadata_collection


def build_country_code_to_region_code_map(metadata_collection):
    """Build a mapping from a country calling code to the region codes which
    denote the country/region represented by that country code. In the case of
    multiple countries sharing a calling code, such as the NANPA countries, the
    one indicated with "is_main_country_for_code" in the metadata should be
    first.
    """
    country_code_to_region_code_map = {}
    for metadata in metadata_collection.metadata:
        region_code = metadata.id
        country_code = metadata.country_code
        if country_code in country_code_to_region_code_map:
            if metadata.main_country_for_code:
                country_code_to_region_code_map[country_code].insert(
                        0, region_code)
            else:
                country_code_to_region_code_map[country_code].append(
                        region_code)
        else:
            # For most countries, there will be only one region code for the
            # country calling code.
            list_with_region_code = []
            list_with_region_code.append(region_code)
            country_code_to_region_code_map[country_code] = \
                    list_with_region_code
    return country_code_to_region_code_map


def _validate_re(regex, remove_whitespace=False):
    # Removes all the whitespace and newline from the regexp. Not using
    # pattern compile options to make it work across programming languages.
    if remove_whitespace:
        regex = re.sub("\\s", "", regex)
    re.compile(regex)
    # Return regex itself if it is of correct regex syntax
    # i.e. compile did not fail with a Pattern_syntax_exception.
    return regex


def _load_country_metadata(region_code, element, metadata):
    metadata.id = region_code
    metadata.country_code = int(element.attrib["countryCode"])
    if "leadingDigits" in element.attrib:
        metadata.leading_digits = _validate_re(element.attrib["leadingDigits"])
    metadata.international_prefix = \
        _validate_re(element.attrib["internationalPrefix"])
    if "preferredInternationalPrefix" in element.attrib:
        preferred_international_prefix = \
                element.attrib["preferredInternationalPrefix"]
        metadata.preferred_international_prefix = \
                preferred_international_prefix

    national_prefix = ""
    national_prefix_formatting_rule = ""
    carrier_code_formatting_rule = ""

    if "nationalPrefixForParsing" in element.attrib:
        metadata.national_prefix_for_parsing = \
                _validate_re(element.attrib["nationalPrefixForParsing"])
        if "nationalPrefixTransformRule" in element.attrib:
            metadata.national_prefix_transform_rule = \
                    _validate_re(element.attrib["nationalPrefixTransformRule"])

    if "nationalPrefix" in element.attrib:
        national_prefix = element.attrib["nationalPrefix"]
        metadata.national_prefix = national_prefix
        national_prefix_formatting_rule = \
                _validate_re(_get_national_prefix_formatting_rule_from_element(
                        element, national_prefix))

        if not metadata.HasField("national_prefix_for_parsing"):
            metadata.national_prefix_for_parsing = national_prefix
    if "preferredExtnPrefix" in element.attrib:
        metadata.preferred_extn_prefix = element.attrib["preferredExtnPrefix"]
    if "mainCountryForCode" in element.attrib:
        metadata.main_country_for_code = True

    # Extract available_formats
    for number_format_element in element.getiterator("numberFormat"):
        format = phonemetadata_pb2.NumberFormat()
        if "nationalPrefixFormattingRule" in number_format_element:
            format.national_prefix_formatting_rule = _validate_re(
                    _get_national_prefix_formatting_rule_from_element(
                            number_format_element, national_prefix))
        else:
            format.national_prefix_formatting_rule = \
                    national_prefix_formatting_rule
        if "carrierCodeFormattingRule" in number_format_element.attrib:
            format.domestic_carrier_code_formatting_rule = _validate_re(
                    _get_domestic_carrier_code_formatting_rule_from_element(
                            number_format_element, national_prefix))
        else:
            format.domestic_carrier_code_formatting_rule = \
                    carrier_code_formatting_rule
        _set_leading_digits_patterns(number_format_element, format)
        format.pattern = _validate_re(number_format_element.attrib["pattern"])
        format_pattern = number_format_element.findall("format")
        if len(format_pattern) != 1:
            logging.warn("Only one format pattern for a numberFormat "
                         "element should be defined.")
            raise Exception("Invalid number of format patterns for "
                            "country: %s" % region_code)
        format.format = _validate_re(format_pattern[0].text)
        metadata.number_format.add().CopyFrom(format)

    for intl_number_format_element in element.getiterator("intlNumberFormat"):
        format = phonemetadata_pb2.NumberFormat()
        _set_leading_digits_patterns(intl_number_format_element, format)
        format.pattern = _validate_re(intl_number_format_element.attrib["pattern"])
        format_pattern = intl_number_format_element.findall("format")
        if len(format_pattern) != 1:
            logging.warn("Only one format pattern for a numberFormat "
                         "element should be defined.")
            raise Exception("Invalid number of format patterns for "
                            "country: %s" % region_code)
        format.format = _validate_re(format_pattern[0].text)
        if "carrierCodeFormattingRule" in intl_number_format_element.attrib:
            format.domestic_carrier_code_formatting_rule = _validate_re(
                    _get_domestic_carrier_code_formatting_rule_from_element(
                            intl_number_format_element, national_prefix))
        else:
            format.domestic_carrier_code_formatting_rule = \
                    carrier_code_formatting_rule
        metadata.intl_number_format.add().CopyFrom(format)

    general_desc = phonemetadata_pb2.PhoneNumberDesc()
    general_desc = _process_phone_number_desc_element(
            general_desc, element, "generalDesc")
    metadata.general_desc.CopyFrom(general_desc)
    metadata.fixed_line.CopyFrom(_process_phone_number_desc_element(
            general_desc, element, "fixedLine"))
    metadata.mobile.CopyFrom(_process_phone_number_desc_element(
            general_desc, element, "mobile"))
    metadata.toll_free.CopyFrom(_process_phone_number_desc_element(
            general_desc, element, "tollFree"))
    metadata.premium_rate.CopyFrom(_process_phone_number_desc_element(
            general_desc, element, "premiumRate"))
    metadata.shared_cost.CopyFrom(_process_phone_number_desc_element(
            general_desc, element, "sharedCost"))
    metadata.voip.CopyFrom(_process_phone_number_desc_element(
            general_desc, element, "voip"))
    metadata.personal_number.CopyFrom(_process_phone_number_desc_element(
            general_desc, element, "personalNumber"))
    metadata.pager.CopyFrom(_process_phone_number_desc_element(
            general_desc, element, "pager"))
    
    if (metadata.mobile.national_number_pattern ==
            metadata.fixed_line.national_number_pattern):
        metadata.same_mobile_and_fixed_line_pattern = True


def _set_leading_digits_patterns(number_format_element, format):
    leading_digits_pattern_nodes = \
            number_format_element.getiterator("leadingDigits")
    for leading_digits_pattern_node in leading_digits_pattern_nodes:
        format.leading_digits_pattern.append(_validate_re(
            leading_digits_pattern_node.text, True))


def _get_national_prefix_formatting_rule_from_element(element,
                                                      national_prefix):
    national_prefix_formatting_rule = \
            element.attrib.get("nationalPrefixFormattingRule", "")
    # Replace $NP with national prefix and $FG with the first group ($1).
    national_prefix_formatting_rule = \
            re.sub("\\$NP", national_prefix, national_prefix_formatting_rule, 1)
    national_prefix_formatting_rule = \
            re.sub("\\$FG", "\\$1", national_prefix_formatting_rule, 1)
    return national_prefix_formatting_rule


def _get_domestic_carrier_code_formatting_rule_from_element(element,
                                                            national_prefix):
    carrier_code_formatting_rule = element.attrib["carrierCodeFormattingRule"]
    # Replace $FG with the first group ($1) and $NP with the national prefix.
    carrier_code_formatting_rule = \
            re.sub("\\$FG", "\\$1", carrier_code_formatting_rule, 1)
    carrier_code_formatting_rule = \
            re.sub("\\$NP", national_prefix, carrier_code_formatting_rule, 1)
    return carrier_code_formatting_rule


def _process_phone_number_desc_element(general_desc, country_element, number_type):
    """Processes a phone number description element from the XML file and
    returns it as a PhoneNumberDesc.

    If the description element is a fixed line or mobile number, the general
    description will be used to fill in the whole element if necessary, or any
    components that are missing. For all other types, the general description
    will only be used to fill in missing components if the type has a partial
    definition. For example, if no "tollFree" element exists, we assume there
    are no toll free numbers for that locale, and return a phone number
    description with "NA" for both the national and possible number patterns.

    Args:
        general_desc: a generic phone number description that will be used to
            fill in missing parts of the description
        country_element: the XML element representing all the country
            information
        number_type: the name of the number type, corresponding to the
                appropriate tag in the XML file with information about that type

    Returns:
        complete description of that phone number type
    """
    phone_number_desc_list = country_element.findall(number_type)
    number_desc = phonemetadata_pb2.PhoneNumberDesc()

    if (not phone_number_desc_list and
        (number_type != "fixedLine" and number_type != "mobile") and
        number_type != "generalDesc"):
        number_desc.national_number_pattern = "NA"
        number_desc.possible_number_pattern = "NA"
        return number_desc

    number_desc.MergeFrom(general_desc)
    if phone_number_desc_list:
        element = phone_number_desc_list[0]
        possible_pattern = element.findall("possibleNumberPattern")
        if possible_pattern:
            number_desc.possible_number_pattern = \
                    _validate_re(possible_pattern[0].text, True)

        valid_pattern = element.findall("nationalNumberPattern")
        if valid_pattern:
            number_desc.national_number_pattern = \
                    _validate_re(valid_pattern[0].text, True)
        if _lite_build:
            example_number = element.findall("exampleNumber")
            if example_number:
                number_desc.example_number = example_number[0].text
    return number_desc


if __name__ == "__main__":
    metadata_collection = \
            build_phone_metadata_collection("PhoneNumberMetaData.xml", False)
    for metadata in metadata_collection.metadata:
        print metadata
    country_code_to_region_code_map = \
            build_country_code_to_region_code_map(metadata_collection)
    print country_code_to_region_code_map
