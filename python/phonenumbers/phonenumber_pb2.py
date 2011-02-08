# Generated by the protocol buffer compiler.  DO NOT EDIT!

from google.protobuf import descriptor
from google.protobuf import message
from google.protobuf import reflection
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)


DESCRIPTOR = descriptor.FileDescriptor(
  name='phonenumber.proto',
  package='i18n.phonenumbers',
  serialized_pb='\n\x11phonenumber.proto\x12\x11i18n.phonenumbers\"\xdc\x02\n\x0bPhoneNumber\x12\x14\n\x0c\x63ountry_code\x18\x01 \x02(\x05\x12\x17\n\x0fnational_number\x18\x02 \x02(\x04\x12\x11\n\textension\x18\x03 \x01(\t\x12\x1c\n\x14italian_leading_zero\x18\x04 \x01(\x08\x12\x11\n\traw_input\x18\x05 \x01(\t\x12M\n\x13\x63ountry_code_source\x18\x06 \x01(\x0e\x32\x30.i18n.phonenumbers.PhoneNumber.CountryCodeSource\"\x8a\x01\n\x11\x43ountryCodeSource\x12\x1e\n\x1a\x46ROM_NUMBER_WITH_PLUS_SIGN\x10\x01\x12\x18\n\x14\x46ROM_NUMBER_WITH_IDD\x10\x05\x12!\n\x1d\x46ROM_NUMBER_WITHOUT_PLUS_SIGN\x10\n\x12\x18\n\x14\x46ROM_DEFAULT_COUNTRY\x10\x14\x42 \n\x1c\x63om.google.i18n.phonenumbersH\x03')



_PHONENUMBER_COUNTRYCODESOURCE = descriptor.EnumDescriptor(
  name='CountryCodeSource',
  full_name='i18n.phonenumbers.PhoneNumber.CountryCodeSource',
  filename=None,
  file=DESCRIPTOR,
  values=[
    descriptor.EnumValueDescriptor(
      name='FROM_NUMBER_WITH_PLUS_SIGN', index=0, number=1,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='FROM_NUMBER_WITH_IDD', index=1, number=5,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='FROM_NUMBER_WITHOUT_PLUS_SIGN', index=2, number=10,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='FROM_DEFAULT_COUNTRY', index=3, number=20,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=251,
  serialized_end=389,
)


_PHONENUMBER = descriptor.Descriptor(
  name='PhoneNumber',
  full_name='i18n.phonenumbers.PhoneNumber',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='country_code', full_name='i18n.phonenumbers.PhoneNumber.country_code', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='national_number', full_name='i18n.phonenumbers.PhoneNumber.national_number', index=1,
      number=2, type=4, cpp_type=4, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='extension', full_name='i18n.phonenumbers.PhoneNumber.extension', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='italian_leading_zero', full_name='i18n.phonenumbers.PhoneNumber.italian_leading_zero', index=3,
      number=4, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='raw_input', full_name='i18n.phonenumbers.PhoneNumber.raw_input', index=4,
      number=5, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='country_code_source', full_name='i18n.phonenumbers.PhoneNumber.country_code_source', index=5,
      number=6, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=1,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _PHONENUMBER_COUNTRYCODESOURCE,
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=41,
  serialized_end=389,
)


_PHONENUMBER.fields_by_name['country_code_source'].enum_type = _PHONENUMBER_COUNTRYCODESOURCE
_PHONENUMBER_COUNTRYCODESOURCE.containing_type = _PHONENUMBER;

class PhoneNumber(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _PHONENUMBER
  
  # @@protoc_insertion_point(class_scope:i18n.phonenumbers.PhoneNumber)
  def exactly_same_as(self, other):
    return (other and
            self.country_code == other.country_code and
            self.national_number == other.national_number and
            self.extension == other.extension and
            self.italian_leading_zero == other.italian_leading_zero and
            self.raw_input == other.raw_input and
            self.country_code_source == other.country_code_source)
  

# @@protoc_insertion_point(module_scope)
