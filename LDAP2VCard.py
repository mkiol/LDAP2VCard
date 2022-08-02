#!/usr/bin/env python
# -*- coding: utf-8 -*- 

# Copyright (C) 2014 Michal Kosciesza <michal@mkiol.net>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/. 

import ldap
import base64

LDAP_URL = "ldap://localhost:389/"
LDAP_USER = "cn=manager,dc=example,dc=com"
LDAP_PASSWORD = "secret"
LDAP_BASEDN = "ou=users,dc=example,dc=com"
LDAP_SEARCH_FILTER = "(&(objectCategory=person)(objectClass=user))"
LDAP_RETRIEVE_ATTRIBUTES = ["sn","givenName","displayName","telephoneNumber","mobile","thumbnailPhoto","mail"]
OUTPUT_DIR = "contacts"


def attribute(data, aName):
    if aName in data[0][1]:
        v = data[0][1][aName][0].decode('utf-8', 'ignore')
        if v.startswith("'") & v.endswith("'"):
            v = v[1:-1]
        if aName == "mobile" or aName == "telephoneNumber":
            v = v.replace(" ", "")
            v = v.replace(".", "")
            v = v.replace("-", "")
        return v
    return ""


def binary_attribute(data, aName):
    if aName in data[0][1]:
        return base64.b64encode(data[0][1][aName][0])
    return ""


ldap_connection = ldap.initialize(LDAP_URL)
ldap_connection.simple_bind_s(LDAP_USER, LDAP_PASSWORD)
searchScope = ldap.SCOPE_SUBTREE

try:
    ldap_result_id = ldap_connection.search(LDAP_BASEDN, searchScope, LDAP_SEARCH_FILTER, LDAP_RETRIEVE_ATTRIBUTES)
    result_set = []
    i = 0
    fileName = OUTPUT_DIR + "/ldap-contacts.vcf"
    oFile = open(fileName, "w")
    while 1:
        i = i + 1
        result_type, result_data = ldap_connection.result(ldap_result_id, 0)
        if not result_data:
            break
        else:
            sn = attribute(result_data, "sn")
            gn = attribute(result_data, "givenName")
            tel = attribute(result_data, "telephoneNumber")
            mobile = attribute(result_data, "mobile")
            image = binary_attribute(result_data, "thumbnailPhoto")
            email = attribute(result_data, "mail")
            title = ""  # TODO
            vcard = (
                "BEGIN:VCARD\r\n"
                "VERSION:3.0\r\n"
                "FN;CHARSET=UTF-8:%s %s\r\n"
                "N;CHARSET=UTF-8:%s;%s\r\n"
                "TEL;WORK;VOICE:%s\r\n"
                "TEL;CELL;VOICE:%s\r\n"
                "PHOTO;ENCODING=BASE64;TYPE=JPEG:%s\r\n"
                "TITLE;CHARSET=UTF-8:%s\r\n"
                "EMAIL;INTERNET:%s\r\n"
                "END:VCARD\r\n"
            )
            print(vcard % (gn, sn, sn, gn, tel, mobile, image, title, email))
            oFile.write(vcard % (gn, sn, sn, gn, tel, mobile, image, title, email))
except ldap.LDAPError as e:
    print(e)
finally:
    oFile.close()
