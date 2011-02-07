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

import os.path
import unittest

from phonenumbers import phonenumberutil


TEST_META_DATA_FILE_PREFIX = phonenumberutil.META_DATA_FILE_PREFIX + "_test"


class PhoneNumberUtilTest(unittest.TestCase):
    def test_get_instance_load_US_metadata(self):
        # In Java and JavaScript a singleton class is used. We use a module
        # in Python, so reloading is like getInstance().
        reload(phonenumberutil)
        metadata = phonenumberutil.get_metadata_for_region("US")
        print metadata
        self.assertEquals("US", metadata.id)
        self.assertEquals(1, metadata.country_code);
        self.assertEquals("011", metadata.international_prefix);
        self.assertTrue(metadata.HasField("national_prefix"));
        self.assertEquals(2, len(metadata.number_format));
        self.assertEquals("(\\d{3})(\\d{3})(\\d{4})",
                metadata.number_format[0].pattern);
        self.assertEquals("$1 $2 $3", 
                metadata.number_format[0].format);
        self.assertEquals("[13-9]\\d{9}|2[0-35-9]\\d{8}",
                metadata.general_desc.national_number_pattern);
        self.assertEquals("\\d{7,10}", 
                metadata.general_desc.possible_number_pattern);
        self.assertTrue(metadata.general_desc.exactly_same_as(
                metadata.fixed_line));
        self.assertEquals("\\d{10}", 
                metadata.toll_free.possible_number_pattern);
        self.assertEquals("900\\d{7}", 
                metadata.premium_rate.national_number_pattern);
        # No shared-cost data is available, so it should be initialised to "NA".
        self.assertEquals("NA", 
                metadata.shared_cost.national_number_pattern);
        self.assertEquals("NA", 
                metadata.shared_cost.possible_number_pattern);


if __name__ == "__main__":
    unittest.main()
