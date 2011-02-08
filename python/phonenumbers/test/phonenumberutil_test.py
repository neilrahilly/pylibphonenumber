#!/usr/bin/env python
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

"""Unit tests for phonenumberutil."""

import unittest

from phonenumbers import phonenumber_pb2
from phonenumbers import phonenumberutil


TEST_META_DATA_FILE_PREFIX = phonenumberutil.META_DATA_FILE_PREFIX + "_test"


phonenumberutil.set_file_prefix(TEST_META_DATA_FILE_PREFIX)


class PhoneNumberUtilTest(unittest.TestCase):
    def test_get_instance_load_US_metadata(self):
        # In Java and JavaScript a singleton class is used. We use a module
        # in Python, so import is like getInstance().
        metadata = phonenumberutil.get_metadata_for_region("US")
        self.assertEquals("US", metadata.id)
        self.assertEquals(1, metadata.country_code)
        self.assertEquals("011", metadata.international_prefix)
        self.assertTrue(metadata.HasField("national_prefix"))
        self.assertEquals(2, len(metadata.number_format))
        self.assertEquals("(\\d{3})(\\d{3})(\\d{4})",
                metadata.number_format[0].pattern)
        self.assertEquals("$1 $2 $3", 
                metadata.number_format[0].format)
        self.assertEquals("[13-9]\\d{9}|2[0-35-9]\\d{8}",
                metadata.general_desc.national_number_pattern)
        self.assertEquals("\\d{7,10}", 
                metadata.general_desc.possible_number_pattern)
        self.assertTrue(metadata.general_desc.exactly_same_as(
                metadata.fixed_line))
        self.assertEquals("\\d{10}", 
                metadata.toll_free.possible_number_pattern)
        self.assertEquals("900\\d{7}", 
                metadata.premium_rate.national_number_pattern)
        # No shared-cost data is available, so it should be initialised to "NA".
        self.assertEquals("NA", 
                metadata.shared_cost.national_number_pattern)
        self.assertEquals("NA", 
                metadata.shared_cost.possible_number_pattern)
        
    def test_get_instance_load_DE_metadata(self):
        metadata = phonenumberutil.get_metadata_for_region("DE")
        self.assertEquals("DE", metadata.id)
        self.assertEquals(49, metadata.country_code)
        self.assertEquals("00", metadata.international_prefix)
        self.assertEquals("0", metadata.national_prefix)
        self.assertEquals(5, len(metadata.number_format))
        self.assertEquals(1, 
                len(metadata.number_format[4].leading_digits_pattern))
        self.assertEquals("900", 
                metadata.number_format[4].leading_digits_pattern[0])
        self.assertEquals("(\\d{3})(\\d{3,4})(\\d{4})",
                metadata.number_format[4].pattern)
        self.assertEquals("$1 $2 $3", metadata.number_format[4].format)
        self.assertEquals("(?:[24-6]\\d{2}|3[03-9]\\d|[789](?:[1-9]\\d|0[2-9]))\\d{3,8}",
                metadata.fixed_line.national_number_pattern)
        self.assertEquals("\\d{2,14}", 
                metadata.fixed_line.possible_number_pattern)
        self.assertEquals("30123456", 
                metadata.fixed_line.example_number)
        self.assertEquals("\\d{10}", 
                metadata.toll_free.possible_number_pattern)
        self.assertEquals("900([135]\\d{6}|9\\d{7})", 
                metadata.premium_rate.national_number_pattern)

    def test_get_instance_load_AR_metadata(self):
        metadata = phonenumberutil.get_metadata_for_region("AR")
        self.assertEquals("AR", metadata.id)
        self.assertEquals(54, metadata.country_code)
        self.assertEquals("00", metadata.international_prefix)
        self.assertEquals("0", metadata.national_prefix)
        self.assertEquals("0(?:(11|343|3715)15)?", 
                metadata.national_prefix_for_parsing)
        self.assertEquals("9$1", metadata.national_prefix_transform_rule)
        self.assertEquals("$1 15 $2-$3", metadata.number_format[2].format)
        self.assertEquals("9(\\d{4})(\\d{2})(\\d{4})",
                metadata.number_format[3].pattern)
        self.assertEquals("(9)(\\d{4})(\\d{2})(\\d{4})",
                metadata.intl_number_format[3].pattern)
        self.assertEquals("$1 $2 $3 $4", 
                metadata.intl_number_format[3].format)

    def test_get_length_of_geographical_area_code(self):
        number = phonenumber_pb2.PhoneNumber()
        # Google MTV, which has area code "650".
        number.country_code = 1
        number.national_number = 6502530000
        self.assertEquals(3, 
            phonenumberutil.get_length_of_geographical_area_code(number))
        
        # A North America toll-free number, which has no area code.
        number.country_code = 1
        number.national_number = 8002530000
        self.assertEquals(0, 
            phonenumberutil.get_length_of_geographical_area_code(number))
        
        # An invalid US number (1 digit shorter), which has no area code.
        number.country_code = 1
        number.national_number = 650253000
        self.assertEquals(0, 
            phonenumberutil.get_length_of_geographical_area_code(number))
        
        # Google London, which has area code "20".
        number.country_code = 44
        number.national_number = 2070313000
        self.assertEquals(2, 
            phonenumberutil.get_length_of_geographical_area_code(number))
        
        # A UK mobile phone, which has no area code.
        number.country_code = 44
        number.national_number = 7123456789
        self.assertEquals(0, 
            phonenumberutil.get_length_of_geographical_area_code(number))
        
        # Google Buenos Aires, which has area code "11".
        number.country_code = 54
        number.national_number = 1155303000
        self.assertEquals(2, 
            phonenumberutil.get_length_of_geographical_area_code(number))
        
        # Google Sydney, which has area code "2".
        number.country_code = 61
        number.national_number = 293744000
        self.assertEquals(1, 
            phonenumberutil.get_length_of_geographical_area_code(number))
        
        # Google Singapore. Singapore has no area code and no national prefix.
        number.country_code = 65
        number.national_number = 65218000
        self.assertEquals(0, 
            phonenumberutil.get_length_of_geographical_area_code(number))


if __name__ == "__main__":
    unittest.main()
