#!/usr/bin/env python2




import argparse
from pySMART import Device
import re, sys, os

argp = argparse.ArgumentParser(description=__doc__)
argp.add_argument('-D', '--device', default='/dev/sda')
argp.add_argument('-P', '--percent', default=5)
argp.add_argument('--html', default=False, action="store_true")
argp.add_argument('--noperf', default=False, action="store_true")

args = argp.parse_args()

device = Device(args.device)

attributes = []
for a in device.attributes:
    if a:
        attributes.append(a)

# fill table
# name, type, value, worst, warning, critical, raw, state, thresh
result = []

count_warning = 0
count_critical = 0

for a in attributes:
    warning = None
    critical = None
    thresh = None
    if a.type == "Pre-fail":
        critical = float(a.thresh)
        thresh = critical
        warning = float(a.thresh) + ( (float(a.thresh) / 100) * float(args.percent) )
    else:
        critical = float(a.thresh) - ( (float(a.thresh) / 100) * float(args.percent) )
        warning = float(a.thresh)
        thresh = warning
    state = 3
    if float(a.value) >= warning and float(a.value) >= critical:
        state = 0
    elif float(a.value) < warning and float(a.value) >= critical:
        state = 1
        count_warning = count_warning + 1
    elif float(a.value) <warning and float(a.value) < critical:
        state = 2 
        count_critical = count_critical + 1
    result.append([a.name, a.type, float(a.value), float(a.worst), float(warning), float(critical), a.raw, state, thresh])

# create output
attribute_num = len(result)
count_ok = len(result) - count_warning - count_critical

overall_state = 0
output = "OK: "
o_w = ""
o_c = ""

if count_warning > 0:
    overall_state = 1
    output = "WARNING: "
    o_w = " - " + str(count_warning) + "/" + str(attribute_num) + " WARNING"
if count_critical > 0:
    overall_state = 2
    output = "CRITICAL: "
    o_c = " - " + str(count_critical) + "/" + str(attribute_num) + " CRITICAL"

output = output + str(count_ok) + "/" + str(attribute_num) + " OK" + o_w + o_c
if args.html:
    output = output + "</br>"
else:
    output = output + "\n"

n_r = ["OK", "WARNING", "CRITICAL", "UNKNOWN"]
h_r = ["", "color:orange", "color:red", "color:blue"]

for a in result:
    if args.html:
        output = output + '<p style="' + h_r[a[7]] + '">'

    output = output + a[0] + "(" + a[1] + ") " + n_r[a[7]] + " current: " + str(a[2]) + " worst: " + str(a[3]) + " thresh: " + str(a[8]) + " raw: " + str(a[6])
    if args.html:
        output = output + "</p>"
    else:
        output = output + "\n"
if args.noperf:
    print(output)
    sys.exit(overall_state)

# perfdata

output = output + "|"
for a in result:
    output = output + a[0] + "=" + str(a[2]) + ";" + str(a[4]) + ";" + str(a[5]) + ";" + str(a[3]) + ";" + "" + " "

print(output)
sys.exit(overall_state)

   
