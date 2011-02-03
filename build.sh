cp -f BuildMetadataPythonFromXml.java \
    ../libphonenumber/java/resources/com/google/i18n/phonenumbers/BuildMetadataPythonFromXml.java
cp -f PythonArrayBuilder.java \
    ../libphonenumber/java/resources/com/google/i18n/phonenumbers/PythonArrayBuilder.java
cd ../libphonenumber
ant -f java/build.xml
java -cp java/build/classes \
    com.google.i18n.phonenumbers.BuildMetadataPythonFromXml \
    java/resources/com/google/i18n/phonenumbers/src/PhoneNumberMetaData.xml \
    ../libphonenumber-py/python/phonenumbers/metadata.py false
java -cp java/build/classes \
    com.google.i18n.phonenumbers.BuildMetadataPythonFromXml \
    java/resources/com/google/i18n/phonenumbers/src/PhoneNumberMetaData.xml \
    ../libphonenumber-py/python/phonenumbers/metadatalite.py true
java -cp java/build/classes \
    com.google.i18n.phonenumbers.BuildMetadataPythonFromXml \
    java/resources/com/google/i18n/phonenumbers/test/PhoneNumberMetaDataForTesting.xml \
    ../libphonenumber-py/python/phonenumbers/metadatafortesting.py false

