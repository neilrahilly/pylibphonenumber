# Copyright (C) Neil Rahilly <neilrahilly@gmail.com>
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


"""Generated by BuildMetadataPythonFromXml.java. Do not edit!"""

# A mapping from a country code to the region codes which denote the
# country/region represented by that country code. In the case of multiple
# countries sharing a calling code, such as the NANPA countries, the one
# indicated with "is_main_country_for_code" in the metadata should be first.
country_code_to_region_code_map = {
1:["US","BS"]
,39:["IT"]
,44:["GB"]
,48:["PL"]
,49:["DE"]
,52:["MX"]
,54:["AR"]
,61:["AU"]
,64:["NZ"]
,65:["SG"]
,81:["JP"]
,82:["KR"]
,244:["AO"]
,262:["RE","YT"]
,376:["AD"]
}

# A mapping from a region code to the PhoneMetadata for that region.
country_to_metadata = {
"AD":[None,[None,None,None,None,None,None,None]
,[None,None,None,None,None,None,None]
,[None,None,None,None,None,None,None]
,[None,None,"NA","NA",None,None,None]
,[None,None,"NA","NA",None,None,None]
,[None,None,"NA","NA",None,None,None]
,[None,None,"NA","NA",None,None,None]
,[None,None,"NA","NA",None,None,None]
,"AD",376,"00",None,None,None,None,None,None,1,None,None,[None,None,"NA","NA",None,None,None]
,None,None]
,"AO":[None,[None,None,"[29]\\d{8}","\\d{9}",None,None,None]
,[None,None,"2\\d(?:[26-9]\\d|\\d[26-9])\\d{5}","\\d{9}",None,None,"222123456"]
,[None,None,"9[1-3]\\d{7}","\\d{9}",None,None,"923123456"]
,[None,None,"NA","NA",None,None,None]
,[None,None,"NA","NA",None,None,None]
,[None,None,"NA","NA",None,None,None]
,[None,None,"NA","NA",None,None,None]
,[None,None,"NA","NA",None,None,None]
,"AO",244,"00","0~0",None,None,"0~0",None,None,None,[[None,"(\\d{3})(\\d{3})(\\d{3})","$1 $2 $3",None,"",""]
]
,None,[None,None,"NA","NA",None,None,None]
,None,None]
,"AR":[None,[None,None,"[1-3689]\\d{9,10}","\\d{6,11}",None,None,None]
,[None,None,"[1-3]\\d{9}","\\d{6,10}",None,None,None]
,[None,None,"9\\d{10}|[1-3]\\d{9}","\\d{10,11}",None,None,None]
,[None,None,"80\\d{8}","\\d{10}",None,None,None]
,[None,None,"6(0\\d|10)\\d{7}","\\d{10}",None,None,None]
,[None,None,"NA","NA",None,None,None]
,[None,None,"NA","NA",None,None,None]
,[None,None,"NA","NA",None,None,None]
,"AR",54,"00","0",None,None,"0(?:(11|343|3715)15)?","9$1",None,None,[[None,"(\\d{2})(\\d{4})(\\d{4})","$1 $2-$3",["11"]
,"0$1",""]
,[None,"(\\d{4})(\\d{2})(\\d{4})","$1 $2-$3",["1[02-9]|[23]"]
,"0$1",""]
,[None,"9(11)(\\d{4})(\\d{4})","$1 15 $2-$3",["911"]
,"0$1",""]
,[None,"9(\\d{4})(\\d{2})(\\d{4})","$1 $2-$3",["9(?:1[02-9]|[23])"]
,"0$1","$1 $CC"]
,[None,"(\\d{3})(\\d{3})(\\d{4})","$1-$2-$3",["[68]"]
,"0$1",""]
]
,[[None,"(\\d{2})(\\d{4})(\\d{4})","$1 $2-$3",["11"]
,None,""]
,[None,"(\\d{4})(\\d{2})(\\d{4})","$1 $2-$3",["1[02-9]|[23]"]
,None,""]
,[None,"(9)(11)(\\d{4})(\\d{4})","$1 $2 $3 $4",["911"]
,None,""]
,[None,"(9)(\\d{4})(\\d{2})(\\d{4})","$1 $2 $3 $4",["9(?:1[02-9]|[23])"]
,None,""]
,[None,"(\\d{3})(\\d{3})(\\d{4})","$1-$2-$3",["[68]"]
,None,""]
]
,[None,None,"NA","NA",None,None,None]
,None,None]
,"AU":[None,[None,None,"[1-578]\\d{4,14}","\\d{5,15}",None,None,None]
,[None,None,"[2378]\\d{8}","\\d{9}",None,None,None]
,[None,None,"4\\d{8}","\\d{9}",None,None,None]
,[None,None,"1800\\d{6}","\\d{10}",None,None,None]
,[None,None,"190[0126]\\d{6}","\\d{10}",None,None,None]
,[None,None,"NA","NA",None,None,None]
,[None,None,"NA","NA",None,None,None]
,[None,None,"NA","NA",None,None,None]
,"AU",61,"001[12]","0",None,None,"0",None,"0011",None,[[None,"(\\d{4})(\\d{3})(\\d{3})","$1 $2 $3",["1"]
,"$1",""]
,[None,"(\\d{1})(\\d{4})(\\d{4})","$1 $2 $3",["[2-478]"]
,"0$1",""]
]
,None,[None,None,"NA","NA",None,None,None]
,None,None]
,"BS":[None,[None,None,"(242|8(00|66|77|88)|900)\\d{7}","\\d{7,10}",None,None,None]
,[None,None,"242(?:3(?:02|[236][1-9]|4[0-24-9]|5[0-68]|7[3-57]|9[2-5])|4(?:2[237]|51|64|77)|502|636|702)\\d{4}","\\d{7,10}",None,None,None]
,[None,None,"242(357|359|457|557)\\d{4}","\\d{10}",None,None,None]
,[None,None,"8(00|66|77|88)\\d{7}","\\d{10}",None,None,None]
,[None,None,"900\\d{7}","\\d{10}",None,None,None]
,[None,None,"NA","NA",None,None,None]
,[None,None,"NA","NA",None,None,None]
,[None,None,"NA","NA",None,None,None]
,"BS",1,"011","1",None,None,"1",None,None,None,None,None,[None,None,"NA","NA",None,None,None]
,None,None]
,"DE":[None,[None,None,"\\d{4,14}","\\d{2,14}",None,None,None]
,[None,None,"(?:[24-6]\\d{2}|3[03-9]\\d|[789](?:[1-9]\\d|0[2-9]))\\d{3,8}","\\d{2,14}",None,None,"30123456"]
,[None,None,"1(5\\d{9}|7\\d{8}|6[02]\\d{8}|63\\d{7})","\\d{10,11}",None,None,None]
,[None,None,"800\\d{7}","\\d{10}",None,None,None]
,[None,None,"900([135]\\d{6}|9\\d{7})","\\d{10,11}",None,None,None]
,[None,None,"NA","NA",None,None,None]
,[None,None,"NA","NA",None,None,None]
,[None,None,"NA","NA",None,None,None]
,"DE",49,"00","0",None,None,"0",None,None,None,[[None,"(\\d{3})(\\d{3,8})","$1 $2",["2|3[3-9]|906|[4-9][1-9]1"]
,"0$1",""]
,[None,"(\\d{2})(\\d{4,9})","$1 $2",["[34]0|[68]9"]
,"0$1",""]
,[None,"([4-9]\\d{3})(\\d{2,7})","$1 $2",["[4-9]","[4-6]|[7-9](?:\\d[1-9]|[1-9]\\d)"]
,"0$1",""]
,[None,"(\\d{3})(\\d{1})(\\d{6})","$1 $2 $3",["800"]
,"0$1",""]
,[None,"(\\d{3})(\\d{3,4})(\\d{4})","$1 $2 $3",["900"]
,"0$1",""]
]
,None,[None,None,"NA","NA",None,None,None]
,None,None]
,"GB":[None,[None,None,"\\d{10}","\\d{6,10}",None,None,None]
,[None,None,"[1-6]\\d{9}","\\d{6,10}",None,None,None]
,[None,None,"7[1-57-9]\\d{8}","\\d{10}",None,None,None]
,[None,None,"80\\d{8}","\\d{10}",None,None,None]
,[None,None,"9[018]\\d{8}","\\d{10}",None,None,None]
,[None,None,"8(?:4[3-5]|7[0-2])\\d{7}","\\d{10}",None,None,None]
,[None,None,"70\\d{8}","\\d{10}",None,None,None]
,[None,None,"56\\d{8}","\\d{10}",None,None,None]
,"GB",44,"00","0",None,None,"0",None,None,None,[[None,"(\\d{2})(\\d{4})(\\d{4})","$1 $2 $3",["[1-59]|[78]0"]
,"(0$1)",""]
,[None,"(\\d)(\\d{3})(\\d{3})(\\d{3})","$1 $2 $3 $4",["6"]
,"(0$1)",""]
,[None,"(\\d{4})(\\d{3})(\\d{3})","$1 $2 $3",["7[1-57-9]"]
,"(0$1)",""]
,[None,"(\\d{3})(\\d{3})(\\d{4})","$1 $2 $3",["8[47]"]
,"(0$1)",""]
]
,None,[None,None,"NA","NA",None,None,None]
,None,None]
,"IT":[None,[None,None,"[0389]\\d{5,10}","\\d{6,11}",None,None,None]
,[None,None,"0\\d{9,10}","\\d{10,11}",None,None,None]
,[None,None,"3\\d{8,9}","\\d{9,10}",None,None,None]
,[None,None,"80(?:0\\d{6}|3\\d{3})","\\d{6,9}",None,None,None]
,[None,None,"89(?:2\\d{3}|9\\d{6})","\\d{6,9}",None,None,None]
,[None,None,"NA","NA",None,None,None]
,[None,None,"NA","NA",None,None,None]
,[None,None,"NA","NA",None,None,None]
,"IT",39,"00",None,None,None,None,None,None,None,[[None,"(\\d{2})(\\d{4})(\\d{4})","$1 $2 $3",["0[26]"]
,"",""]
,[None,"(\\d{3})(\\d{4})(\\d{3,4})","$1 $2 $3",["0[13-57-9]"]
,"",""]
,[None,"(\\d{3})(\\d{3})(\\d{3,4})","$1 $2 $3",["3"]
,"",""]
,[None,"(\\d{3})(\\d{3,6})","$1 $2",["8"]
,"",""]
]
,None,[None,None,"NA","NA",None,None,None]
,None,None]
,"JP":[None,[None,None,None,None,None,None,None]
,[None,None,None,None,None,None,None]
,[None,None,None,None,None,None,None]
,[None,None,"NA","NA",None,None,None]
,[None,None,"NA","NA",None,None,None]
,[None,None,"NA","NA",None,None,None]
,[None,None,"NA","NA",None,None,None]
,[None,None,"NA","NA",None,None,None]
,"JP",81,"010","0",None,None,"0",None,None,1,[[None,"(\\d{2})(\\d{4})(\\d{4})","$1 $2 $3",["[57-9]0"]
,"0$1",""]
,[None,"(\\d{2})(\\d{3})(\\d{4})","$1 $2 $3",["222|333","(?:222|333)1","(?:222|333)11"]
,"0$1",""]
,[None,"(\\d{4})(\\d)(\\d{4})","$1 $2 $3",["222|333","2221|3332","22212|3332","222120|3332"]
,"0$1",""]
,[None,"(\\d{3})(\\d{2})(\\d{4})","$1 $2 $3",["[23]"]
,"0$1",""]
]
,None,[None,None,"NA","NA",None,None,None]
,None,None]
,"KR":[None,[None,None,"[1-79]\\d{3,9}|8\\d{8}","\\d{4,10}",None,None,None]
,[None,None,"(?:2|[34][1-3]|5[1-5]|6[1-4])(?:1\\d{2,3}|[2-9]\\d{6,7})","\\d{4,10}",None,None,"22123456"]
,[None,None,"1[0-25-9]\\d{7,8}","\\d{9,10}",None,None,"1023456789"]
,[None,None,"80\\d{7}","\\d{9}",None,None,"801234567"]
,[None,None,"60[2-9]\\d{6}","\\d{9}",None,None,"602345678"]
,[None,None,"NA","NA",None,None,None]
,[None,None,"50\\d{8}","\\d{10}",None,None,"5012345678"]
,[None,None,"70\\d{8}","\\d{10}",None,None,"7012345678"]
,"KR",82,"00(?:[124-68]|[37]\\d{2})","0",None,None,"0(?:8[1-46-8]|85\\d{2})?",None,None,None,[[None,"(\\d{2})(\\d{4})(\\d{4})","$1-$2-$3",["1(?:0|1[19]|[69]9|5[458])|[57]0","1(?:0|1[19]|[69]9|5(?:44|59|8))|[57]0"]
,"0$1",""]
,[None,"(\\d{2})(\\d{3})(\\d{4})","$1-$2-$3",["1(?:[169][2-8]|[78]|5[1-4])|[68]0|[3-9][1-9][2-9]","1(?:[169][2-8]|[78]|5(?:[1-3]|4[56]))|[68]0|[3-9][1-9][2-9]"]
,"0$1",""]
,[None,"(\\d{3})(\\d)(\\d{4})","$1-$2-$3",["131","1312"]
,"0$1",""]
,[None,"(\\d{3})(\\d{2})(\\d{4})","$1-$2-$3",["131","131[13-9]"]
,"0$1",""]
,[None,"(\\d{3})(\\d{3})(\\d{4})","$1-$2-$3",["13[2-9]"]
,"0$1",""]
,[None,"(\\d{2})(\\d{2})(\\d{3})(\\d{4})","$1-$2-$3-$4",["30"]
,"0$1",""]
,[None,"(\\d)(\\d{4})(\\d{4})","$1-$2-$3",["2(?:[26]|3[0-467])","2(?:[26]|3(?:01|1[45]|2[17-9]|39|4|6[67]|7[078]))"]
,"0$1",""]
,[None,"(\\d)(\\d{3})(\\d{4})","$1-$2-$3",["2(?:3[0-35-9]|[457-9])","2(?:3(?:0[02-9]|1[0-36-9]|2[02-6]|3[0-8]|6[0-589]|7[1-69]|[589])|[457-9])"]
,"0$1",""]
,[None,"(\\d)(\\d{3})","$1-$2",["21[0-46-9]","21(?:[0-247-9]|3[124]|6[1269])"]
,"0$1",""]
,[None,"(\\d)(\\d{4})","$1-$2",["21[36]","21(?:3[035-9]|6[03-578])"]
,"0$1",""]
,[None,"(\\d{2})(\\d{3})","$1-$2",["[3-9][1-9]1","[3-9][1-9]1(?:[0-46-9])","[3-9][1-9]1(?:[0-247-9]|3[124]|6[1269])"]
,"0$1",""]
,[None,"(\\d{2})(\\d{4})","$1-$2",["[3-9][1-9]1","[3-9][1-9]1[36]","[3-9][1-9]1(?:3[035-9]|6[03-578])"]
,"0$1",""]
]
,None,[None,None,"NA","NA",None,None,None]
,None,None]
,"MX":[None,[None,None,"[1-9]\\d{9,10}","\\d{7,11}",None,None,None]
,[None,None,"[2-9]\\d{9}","\\d{7,10}",None,None,None]
,[None,None,"1\\d{10}","\\d{11}",None,None,None]
,[None,None,"800\\d{7}","\\d{10}",None,None,None]
,[None,None,"900\\d{7}","\\d{10}",None,None,None]
,[None,None,"NA","NA",None,None,None]
,[None,None,"NA","NA",None,None,None]
,[None,None,"NA","NA",None,None,None]
,"MX",52,"00","01",None,None,"01|04[45](\\d{10})","1$1",None,None,[[None,"(\\d{3})(\\d{3})(\\d{4})","$1 $2 $3",["[89]00"]
,"",""]
,[None,"(\\d{2})(\\d{4})(\\d{4})","$1 $2 $3",["33|55|81"]
,"",""]
,[None,"(\\d{3})(\\d{3})(\\d{4})","$1 $2 $3",["[2467]|3[0-24-9]|5[0-46-9]|8[2-9]|9[1-9]"]
,"",""]
,[None,"1(\\d{2})(\\d{4})(\\d{4})","045 $1 $2 $3",["1(?:33|55|81)"]
,"",""]
,[None,"1(\\d{3})(\\d{3})(\\d{4})","045 $1 $2 $3",["1(?:[124579]|3[0-24-9]|5[0-46-9]|8[02-9])"]
,"",""]
]
,[[None,"(\\d{3})(\\d{3})(\\d{4})","$1 $2 $3",["[89]00"]
,None,""]
,[None,"(\\d{2})(\\d{4})(\\d{4})","$1 $2 $3",["33|55|81"]
,None,""]
,[None,"(\\d{3})(\\d{3})(\\d{4})","$1 $2 $3",["[2467]|3[0-24-9]|5[0-46-9]|8[2-9]|9[1-9]"]
,None,""]
,[None,"(1)(\\d{2})(\\d{4})(\\d{4})","$1 $2 $3 $4",["1(?:33|55|81)"]
,None,""]
,[None,"(1)(\\d{3})(\\d{3})(\\d{4})","$1 $2 $3 $4",["1(?:[124579]|3[0-24-9]|5[0-46-9]|8[02-9])"]
,None,""]
]
,[None,None,"NA","NA",None,None,None]
,None,None]
,"NZ":[None,[None,None,"[2-9]\\d{7,9}","\\d{7,10}",None,None,None]
,[None,None,"24099\\d{3}|(?:3[2-79]|[479][2-689]|6[235-9])\\d{6}","\\d{7,8}",None,None,None]
,[None,None,"2(?:[027]\\d{7}|9\\d{6,7}|1(?:0\\d{5,7}|[12]\\d{5,6}|[3-9]\\d{5})|4[1-9]\\d{6}|8\\d{7,8})","\\d{8,10}",None,None,None]
,[None,None,"800\\d{6,7}","\\d{9,10}",None,None,None]
,[None,None,"900\\d{6,7}","\\d{9,10}",None,None,None]
,[None,None,"NA","NA",None,None,None]
,[None,None,"NA","NA",None,None,None]
,[None,None,"NA","NA",None,None,None]
,"NZ",64,"00","0",None,None,"0",None,None,None,[[None,"(\\d)(\\d{3})(\\d{4})","$1-$2 $3",["24|[34679]"]
,"0$1",""]
,[None,"(\\d)(\\d{3})(\\d{3,5})","$1-$2 $3",["2[179]"]
,"0$1",""]
,[None,"(\\d{3})(\\d{3})(\\d{3,4})","$1 $2 $3",["[89]"]
,"0$1",""]
]
,None,[None,None,"NA","NA",None,None,None]
,None,None]
,"PL":[None,[None,None,"[1-9]\\d{8}","\\d{9}",None,None,None]
,[None,None,"[1-9]\\d{8}","\\d{9}",None,None,None]
,[None,None,"(?:5[01]|6[069]|7[289]|88)\\d{7}","\\d{9}",None,None,None]
,[None,None,"800\\d{6}","\\d{9}",None,None,None]
,[None,None,"70\\d{7}","\\d{9}",None,None,None]
,[None,None,"NA","NA",None,None,None]
,[None,None,"NA","NA",None,None,None]
,[None,None,"NA","NA",None,None,None]
,"PL",48,"0~0","0",None,None,"0",None,None,None,[[None,"(\\d{2})(\\d{3})(\\d{2})(\\d{2})","$1 $2 $3 $4",None,"0$1",""]
]
,None,[None,None,"NA","NA",None,None,None]
,None,None]
,"RE":[None,[None,None,"[268]\\d{8}","\\d{9}",None,None,None]
,[None,None,"262\\d{6}","\\d{9}",None,None,"262161234"]
,[None,None,"6(?:9[23]|47)\\d{6}","\\d{9}",None,None,"692123456"]
,[None,None,"80\\d{7}","\\d{9}",None,None,"801234567"]
,[None,None,"8(?:1[01]|2[0156]|84|9[0-37-9])\\d{6}","\\d{9}",None,None,"810123456"]
,[None,None,"NA","NA",None,None,None]
,[None,None,"NA","NA",None,None,None]
,[None,None,"NA","NA",None,None,None]
,"RE",262,"00","0",None,None,"0",None,None,None,[[None,"([268]\\d{2})(\\d{2})(\\d{2})(\\d{2})","$1 $2 $3 $4",None,"0$1",""]
]
,None,[None,None,"NA","NA",None,None,None]
,None,"262|6(?:9[23]|47)|8"]
,"SG":[None,[None,None,"[13689]\\d{7,10}","\\d{8,11}",None,None,None]
,[None,None,"[36]\\d{7}","\\d{8}",None,None,None]
,[None,None,"[89]\\d{7}","\\d{8}",None,None,None]
,[None,None,"1?800\\d{7}","\\d{10,11}",None,None,None]
,[None,None,"1900\\d{7}","\\d{11}",None,None,None]
,[None,None,"NA","NA",None,None,None]
,[None,None,"NA","NA",None,None,None]
,[None,None,"NA","NA",None,None,None]
,"SG",65,"0[0-3][0-9]",None,None,None,None,None,None,None,[[None,"(\\d{4})(\\d{4})","$1 $2",["[369]|8[1-9]"]
,"",""]
,[None,"(\\d{4})(\\d{3})(\\d{4})","$1 $2 $3",["1[89]"]
,"",""]
,[None,"(\\d{3})(\\d{3})(\\d{4})","$1 $2 $3",["800"]
,"",""]
]
,None,[None,None,"NA","NA",None,None,None]
,None,None]
,"US":[None,[None,None,"[13-9]\\d{9}|2[0-35-9]\\d{8}","\\d{7,10}",None,None,"1234567890"]
,[None,None,"[13-9]\\d{9}|2[0-35-9]\\d{8}","\\d{7,10}",None,None,"1234567890"]
,[None,None,"[13-9]\\d{9}|2[0-35-9]\\d{8}","\\d{7,10}",None,None,"1234567890"]
,[None,None,"8(00|66|77|88)\\d{7}","\\d{10}",None,None,"1234567890"]
,[None,None,"900\\d{7}","\\d{10}",None,None,"1234567890"]
,[None,None,"NA","NA",None,None,None]
,[None,None,"NA","NA",None,None,None]
,[None,None,"NA","NA",None,None,None]
,"US",1,"011","1"," extn. ",None,"1",None,None,1,[[None,"(\\d{3})(\\d{3})(\\d{4})","$1 $2 $3",None,"",""]
,[None,"(\\d{3})(\\d{4})","$1 $2",None,"",""]
]
,[[None,"(\\d{3})(\\d{3})(\\d{4})","$1 $2 $3",None,None,""]
]
,[None,None,"NA","NA",None,None,None]
,1,None]
,"YT":[None,[None,None,"[268]\\d{8}","\\d{9}",None,None,None]
,[None,None,"2696[0-4]\\d{4}","\\d{9}",None,None,"269601234"]
,[None,None,"639\\d{6}","\\d{9}",None,None,"639123456"]
,[None,None,"80\\d{7}","\\d{9}",None,None,"801234567"]
,[None,None,"NA","NA",None,None,None]
,[None,None,"NA","NA",None,None,None]
,[None,None,"NA","NA",None,None,None]
,[None,None,"NA","NA",None,None,None]
,"YT",262,"00","0",None,None,"0",None,None,None,None,None,[None,None,"NA","NA",None,None,None]
,None,"269|639"]
}

