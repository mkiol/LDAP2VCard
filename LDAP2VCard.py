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

def getAttribute(data, aName):
	if aName in data[0][1]:
		v = data[0][1][aName][0].decode('utf-8', 'ignore')
		if aName == "mobile" or aName == "telephoneNumber":
			v = v.replace(" ", "")
			v = v.replace(".", "")
			v = v.replace("-", "")
		return v.encode('utf-8', 'ignore')
	return ""

def getBinaryAttribute(data, aName):
	if aName in data[0][1]:
		return base64.b64encode(data[0][1][aName][0])
	return ""

l = ldap.initialize(LDAP_URL)
l.simple_bind_s(LDAP_USER,LDAP_PASSWORD)
searchScope = ldap.SCOPE_SUBTREE

try:
	ldap_result_id = l.search(LDAP_BASEDN, searchScope, LDAP_SEARCH_FILTER, LDAP_RETRIEVE_ATTRIBUTES)
	result_set = []
	while 1:
		i=i+1
		result_type, result_data = l.result(ldap_result_id, 0)
		if (result_data == []):
			break
		else:
			sn = getAttribute(result_data,"sn")
			gn = getAttribute(result_data,"givenName")
			tel = getAttribute(result_data,"telephoneNumber")
			mobile = getAttribute(result_data,"mobile")
			image = getBinaryAttribute(result_data,"thumbnailPhoto")
			email = getAttribute(result_data,"mail")
			vcard = (
				"BEGIN:VCARD\r\nVERSION:3.0\r\n"
				"FN;CHARSET=UTF-8:%s %s\r\nN;CHARSET=UTF-8:%s;%s\r\nTEL;WORK;VOICE:%s\r\n"
				"TEL;CELL;VOICE:%s\r\nPHOTO;ENCODING=BASE64;TYPE=JPEG:%s\r\n"
				"TITLE;CHARSET=UTF-8:%s\r\nEMAIL;INTERNET:%s\r\n"
				"END:VCARD\r\n"
			)
			fileName = OUTPUT_DIR+"/%s.vcf" % (sn+" "+gn)
			oFile = open(fileName.decode('utf-8', 'ignore'), "w")
			oFile.write(vcard % (gn,sn,sn,gn,tel,mobile,image,title,email))
			oFile.close()
			
except ldap.LDAPError, e:
	print e

