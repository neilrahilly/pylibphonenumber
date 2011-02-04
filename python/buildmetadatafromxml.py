#!/usr/bin/env python

"""Library to build phone number metadata from the XML format.

Based on BuildMetadataFromXml.java.
"""

import logging
import re
import xml.etree.ElementTree

from phonenumbers import phonemetadata_pb2


def build_phone_metadata_collection(input_xml_file, lite_build):
    """Build the PhoneMetadataCollection from the input XML file."""
    tree = xml.etree.ElementTree.parse(input_xml_file)
    metadata_collection = phonemetadata_pb2.PhoneMetadataCollection()
    for territory in tree.getiterator("territory"):
        metadata = metadata_collection.metadata.add()
        region_code = territory.attrib["id"]
        _load_country_metadata(region_code, territory, metadata)
    return metadata_collection 

#  // Build a mapping from a country calling code to the region codes which denote the country/region
#  // represented by that country code. In the case of multiple countries sharing a calling code,
#  // such as the NANPA countries, the one indicated with "is_main_country_for_code" in the metadata
#  // should be first.
#  public static Map<Integer, List<String>> build_country_code_to_region_code_map(
#      Phone_metadata_collection metadata_collection) {
#    Map<Integer, List<String>> country_code_to_region_code_map =
#        new Tree_map<Integer, List<String>>()
#    for (Phone_metadata metadata : metadata_collection.get_metadata_list()) {
#      String region_code = metadata.get_id()
#      int country_code = metadata.get_country_code()
#      if (country_code_to_region_code_map.contains_key(country_code)) {
#        if (metadata.get_main_country_for_code()) {
#          country_code_to_region_code_map.get(country_code).add(0, region_code)
#        } else {
#          country_code_to_region_code_map.get(country_code).add(region_code)
#        }
#      } else {
#        // For most countries, there will be only one region code for the country calling code.
#        List<String> list_with_region_code = new Array_list<String>(1)
#        list_with_region_code.add(region_code)
#        country_code_to_region_code_map.put(country_code, list_with_region_code)
#      }
#    }
#    return country_code_to_region_code_map
#  }
#

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
#    metadata = phonemetadata_pb2.PhoneMetadata()
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
    
#
    # Extract available_formats
    
    number_format_elements = element.getiterator("numberFormat")
    for number_format_element in number_format_elements:
        format = phonemetadata_pb2.NumberFormat()
        if "nationalPrefixFormattingRule" in number_format_element:
            format.national_prefix_formatting_rule = _validate_re(
                    _get_national_prefix_formatting_rule_from_element(
                            number_format_element, national_prefix))
        else:
            format.national_prefix_formatting_rule = national_prefix_formatting_rule
        if "carrierCodeFormattingRule" in number_format_element.attrib:
            format.domestic_carrier_code_formatting_rule = _validate_re(
                    _get_domestic_carrier_code_formatting_rule_from_element(
                            number_format_element, national_prefix))
        else:
            format.domestic_carrier_code_formatting_rule = carrier_code_formatting_rule
        _set_leading_digits_patterns(number_format_element, format)
        format.pattern = _validate_re(number_format_element.attrib["pattern"])
        format_pattern = number_format_element.getiterator("format")
        if len(format_pattern) != 1:
            logging.warn("Only one format pattern for a number_format "
                         "element should be defined.")
            raise Exception("Invalid number of format patterns for "
                            "country: %s" % region_code)
        format.format = _validate_re(format_pattern.item(0).get_first_child().get_node_value())
        metadata.add_number_format(format)
#
#    Node_list intl_number_format_elements = element.get_elements_by_tag_name("intl_number_format")
#    int num_of_intl_format_elements = intl_number_format_elements.get_length()
#    if (num_of_intl_format_elements > 0) {
#        for (int i = 0; i < num_of_intl_format_elements; i++) {
#            Element number_format_element = (Element) intl_number_format_elements.item(i)
#            Number_format format = new Number_format()
#            set_leading_digits_patterns(number_format_element, format)
#            format.set_pattern(_validate_re(number_format_element.get_attribute("pattern")))
#            Node_list format_pattern = number_format_element.get_elements_by_tag_name("format")
#            if (format_pattern.get_length() != 1) {
#                LOGGER.log(Level.SEVERE,
#                                     "Only one format pattern for a number_format element should be defined.")
#                throw new Runtime_exception("Invalid number of format patterns for country: " +
#                                                                     region_code)
#            }
#            format.set_format(_validate_re(format_pattern.item(0).get_first_child().get_node_value()))
#            if (number_format_element.has_attribute("carrier_code_formatting_rule")) {
#                format.set_domestic_carrier_code_formatting_rule(_validate_re(
#                        get_domestic_carrier_code_formatting_rule_from_element(number_format_element,
#                                                                                                                        national_prefix)))
#            } else {
#                format.set_domestic_carrier_code_formatting_rule(carrier_code_formatting_rule)
#            }
#            metadata.add_intl_number_format(format)
#        }
#    }
#
#    Phone_number_desc general_desc = new Phone_number_desc()
#    general_desc = process_phone_number_desc_element(general_desc, element, "general_desc")
#    metadata.set_general_desc(general_desc)
#    metadata.set_fixed_line(process_phone_number_desc_element(general_desc, element, "fixed_line"))
#    metadata.set_mobile(process_phone_number_desc_element(general_desc, element, "mobile"))
#    metadata.set_toll_free(process_phone_number_desc_element(general_desc, element, "toll_free"))
#    metadata.set_premium_rate(process_phone_number_desc_element(general_desc, element, "premium_rate"))
#    metadata.set_shared_cost(process_phone_number_desc_element(general_desc, element, "shared_cost"))
#    metadata.set_voip(process_phone_number_desc_element(general_desc, element, "voip"))
#    metadata.set_personal_number(process_phone_number_desc_element(general_desc, element,
#                                                                                                                     "personal_number"))
#    metadata.set_pager(process_phone_number_desc_element(general_desc, element, "pager"))
#
#    if (metadata.get_mobile().get_national_number_pattern().equals(
#            metadata.get_fixed_line().get_national_number_pattern())) {
#        metadata.set_same_mobile_and_fixed_line_pattern(true)
#    }
#    return metadata
#}
#
def _set_leading_digits_patterns(number_format_element, format):
    for leading_digits_pattern_node in number_format_element.getiterator("leadingDigits"):
        # FIXME: This is almost definitely fucked up in here
        
        format.add_leading_digits_pattern(_validate_re(
            leading_digits_pattern_node.firstchild().value(), True))


def _get_national_prefix_formatting_rule_from_element(element, national_prefix):
    national_prefix_formatting_rule = element.attrib.get("nationalPrefixFormattingRule", "")
    # Replace $NP with national prefix and $FG with the first group ($1).
    national_prefix_formatting_rule = \
            re.sub("\\$NP", national_prefix, national_prefix_formatting_rule, 1)
    national_prefix_formatting_rule = \
            re.sub("\\$FG", "\\$1", national_prefix_formatting_rule, 1)
    return national_prefix_formatting_rule
#
#private static String get_domestic_carrier_code_formatting_rule_from_element(Element element,
#                                                                                                                                            String national_prefix) {
#    String carrier_code_formatting_rule = element.get_attribute("carrier_code_formatting_rule")
#    // Replace $FG with the first group ($1) and $NP with the national prefix.
#    carrier_code_formatting_rule = carrier_code_formatting_rule.replace_first("\\$FG", "\\$1")
#            .replace_first("\\$NP", national_prefix)
#    return carrier_code_formatting_rule
#}
#
#/**
# * Processes a phone number description element from the XML file and returns it as a
# * Phone_number_desc. If the description element is a fixed line or mobile number, the general
# * description will be used to fill in the whole element if necessary, or any components that are
# * missing. For all other types, the general description will only be used to fill in missing
# * components if the type has a partial definition. For example, if no "toll_free" element exists,
# * we assume there are no toll free numbers for that locale, and return a phone number description
# * with "NA" for both the national and possible number patterns.
# *
# * @param general_desc  a generic phone number description that will be used to fill in missing
# *                                       parts of the description
# * @param country_element    the XML element representing all the country information
# * @param number_type    the name of the number type, corresponding to the appropriate tag in the XML
# *                                      file with information about that type
# * @return  complete description of that phone number type
# */
#private static Phone_number_desc process_phone_number_desc_element(Phone_number_desc general_desc,
#                                                                                                                         Element country_element,
#                                                                                                                         String number_type) {
#    Node_list phone_number_desc_list = country_element.get_elements_by_tag_name(number_type)
#    Phone_number_desc number_desc = new Phone_number_desc()
#    if (phone_number_desc_list.get_length() == 0 &&
#            (!number_type.equals("fixed_line") && !number_type.equals("mobile") &&
#             !number_type.equals("general_desc"))) {
#        number_desc.set_national_number_pattern("NA")
#        number_desc.set_possible_number_pattern("NA")
#        return number_desc
#    }
#    number_desc.merge_from(general_desc)
#    if (phone_number_desc_list.get_length() > 0) {
#        Element element = (Element) phone_number_desc_list.item(0)
#        Node_list possible_pattern = element.get_elements_by_tag_name("possible_number_pattern")
#        if (possible_pattern.get_length() > 0) {
#            number_desc.set_possible_number_pattern(
#                    _validate_re(possible_pattern.item(0).get_first_child().get_node_value(), true))
#        }
#
#        Node_list valid_pattern = element.get_elements_by_tag_name("national_number_pattern")
#        if (valid_pattern.get_length() > 0) {
#            number_desc.set_national_number_pattern(
#                    _validate_re(valid_pattern.item(0).get_first_child().get_node_value(), true))
#        }
#
#        if (!lite_build) {
#            Node_list example_number = element.get_elements_by_tag_name("example_number")
#            if (example_number.get_length() > 0) {
#                number_desc.set_example_number(example_number.item(0).get_first_child().get_node_value())
#            }
#        }
#    }
#    return number_desc
#}
#}

if __name__ == "__main__":
    build_phone_metadata_collection("PhoneNumberMetaData.xml", False)

