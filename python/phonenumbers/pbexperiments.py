#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2010 Atomic Contacts
#
from phonenumbers import phonemetadata_pb2

META_DATA_FILE_PREFIX = "/Users/neil/workspace/libphonenumber-py/python/phonenumbers/data/PhoneNumberMetadataProto"


def _load_metadata_for_region_from_file(file_prefix, region_code):
    f = open(file_prefix + "_" + region_code, "r")
    c = phonemetadata_pb2.PhoneMetadataCollection()
    print dir(c.metadata)
    c.metadata.ParseFromString(f.read())
    print c
#    serialized_metadata_collection = f.read()
#    print serialized_metadata_collection
#    metadata_collection = phonemetadata_pb2.PhoneMetadataCollection()
#    metadata_collection.ParseFromString(serialized_metadata_collection)


if __name__ == "__main__":
    _load_metadata_for_region_from_file(META_DATA_FILE_PREFIX, "US")
