# Copyright (C) 2011 Neil Rahilly <neilrahilly@gmail.com>
# 
# Licensed under the Apache License, Version 2.0 (the "License");
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

"""Constants used by build scripts."""


import os.path


_ROOT = os.path.abspath(os.path.dirname(__file__))

META_DATA_FILE_PREFIX = os.path.join(
        _ROOT, "data", "phonenumbermetadataproto")

TEST_META_DATA_FILE_PREFIX = os.path.join(
        _ROOT, "test", "data", "phonenumbermetadataproto_test")

COUNTRY_CODE_TO_REGION_CODE_MAP_NAME = "country_code_to_region_code_map"
