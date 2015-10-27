#!/usr/bin/python2

import argparse
from pySMART import Device
import re, sys, os

argp = argparse.ArgumentParser(description=__doc__)
argp.add_argument('-D', '--device', default='/dev/sda')
argp.add_argument('-A', '--attributes', default='all')
argp.add_argument('-R', '--raw', default=False, action="store_true")

args = argp.parse_args()

#checks device availability
if not re.match('(\/\w+)+', args.device):
    print("bad device format: %s - devices must be given as absolute path like /dev/sda" % args.device)
    sys.exit(3)
if not os.path.exists(args.device):
    print("bad device: %s - device not found" % args.device)
    sys.exit(3)

# get smart data first
device = Device(args.device)

tmp_attributes = device.attributes
attributes = []
# remove None attributes
for tmp in tmp_attributes:
    if not tmp == None:
        attributes.append(tmp)




req_attributes = args.attributes.split(',')

check_attributes = []
if "all" in req_attributes:
    check_attributes = attributes
else:
    for attribute in attributes:
        for req_attribute in req_attributes:
            if req_attribute == attribute.name:
                check_attributes.append(attribute)


ok = []
warn = []
crit = []


for check_attribute in check_attributes:

    if check_attribute.type == "Pre-fail":
        if int(check_attribute.value) > int(check_attribute.thresh):
            ok.append([check_attribute.name, check_attribute.value, check_attribute.thresh, check_attribute.type, check_attribute.raw, "C"])
        else:
            crit.append([check_attribute.name, check_attribute.value, check_attribute.thresh, check_attribute.type, check_attribute.raw, "C"])
    else:
        if int(check_attribute.value) > int(check_attribute.thresh):
           ok.append([check_attribute.name, check_attribute.value, check_attribute.thresh, check_attribute.type, check_attribute.raw, "W"])
        else:
            warn.append([check_attribute.name, check_attribute.value, check_attribute.thresh, check_attribute.type, check_attribute.raw, "W"])
    
ret = 0
out = "OK"

if len(warn) > 1:
    ret = 1
    out = "WARNING"
if len(crit) > 1:
    ret = 2
    out = "CRITICAL"

retstr = out

for i in crit:
    retstr = retstr + " " + i[0] + "=" + i[1] + "/" + i[2] + " RAW: " + i[4] + ","
for i in warn:
    retstr = retstr + " " + i[0] + "=" + i[1] + "/" + i[2] + " RAW: " + i[4] + ","
for i in ok:
    retstr = retstr + " " + i[0] + "=" + i[1] + "/" + i[2] + " RAW: " + i[4] + ","

retstr = retstr.strip(",")

retstr = retstr + "|"
for i in crit:
    if args.raw:
        retstr = retstr + i[0] + "=" + i[4] + ";;;;"
    if i[5] == "W":
        retstr = retstr + i[0] + "_qual=" + i[1] + ";" + i[2] + ":;;;"
    else:
        retstr = retstr + i[0] + "_qual=" + i[1] + ";;" + i[2] + ":;;"


for i in warn:
    if args.raw:
        retstr = retstr + i[0] + "=" + i[4] + ";;;;"
    if i[5] == "W":
        retstr = retstr + i[0] + "_qual=" + i[1] + ";" + i[2] + ":;;;"
    else:
        retstr = retstr + i[0] + "_qual=" + i[1] + ";;" + i[2] + ":;;"



for i in ok:
    if args.raw:
        retstr = retstr + i[0] + "=" + i[4] + ";;;;"
    if i[5] == "W":
        retstr = retstr + i[0] + "_qual=" + i[1] + ";" + i[2] + ":;;;"
    else:
        retstr = retstr + i[0] + "_qual=" + i[1] + ";;" + i[2] + ":;;"




retstr = retstr.rstrip(";") + ";;;"


print(retstr)
sys.exit(ret)












#    print(check_attribute.name)
#    print(check_attribute.raw)
#    print(check_attribute.type)
#    print(check_attribute.value)
#    print(check_attribute.worst)
#    print(check_attribute.thresh)



