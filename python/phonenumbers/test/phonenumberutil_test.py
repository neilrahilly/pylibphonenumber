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

from phonenumbers import phonenumberutil


class PhoneNumberUtilTest(unittest.TestCase):
    def test_get_instance_load_US_metadata(self):
        # In Java and JavaScript a singleton class is used. We use a module
        # in Python, so reloading is like getInstance().
        reload(phonenumberutil)
        phonenumberutil.get_metadata_for_region("US")
        self.assertEquals("US", metadata.get_id())
        self.assertEquals(1, metadata.get_country_code());
        self.assertEquals("011", metadata.get_international_prefix());
        self.assertTrue(metadata.has_national_prefix());
        self.assertEquals(2, metadata.get_number_format_count());
        self.assertEquals("(\\d{3})(\\d{3})(\\d{4})",
                metadata.get_number_format(0).get_pattern());
        self.assertEquals("$1 $2 $3", 
                metadata.get_number_format(0).get_format());
        self.assertEquals("[13-9]\\d{9}|2[0-35-9]\\d{8}",
                metadata.get_general_desc().get_national_number_pattern());
        self.assertEquals("\\d{7,10}", 
                metadata.get_general_desc().get_possible_number_pattern());
        self.assertTrue(metadata.get_general_desc().exactly_same_as(
                metadata.get_fixed_line()));
        self.assertEquals("\\d{10}", 
                metadata.get_toll_free().get_possible_number_pattern());
        self.assertEquals("900\\d{7}", 
                metadata.get_premium_rate().get_national_number_pattern());
        # No shared-cost data is available, so it should be initialised to "NA".
        self.assertEquals("NA", 
                metadata.get_shared_cost().get_national_number_pattern());
        self.assertEquals("NA", 
                metadata.get_shared_cost().get_possible_number_pattern());


if __name__ == "__main__":
    unittest.main()
