#!/usr/bin/env python

import os, sys, glob, subprocess, shutil, argparse, requests, json, urllib, pprint, time

#################################################################################################
# Usage : If you want to run plenty of sample into Fastqc API, use this script			#
# write /data/Tools/bin/RunFastqc_API_manual.txt						#
# ex) NextSeqDx	200701_NDX550181_0142_AHFT2GAFX2	2020062725749-EF3-LT			#
# $ python RunFastqc_API_manual.py								#
#################################################################################################

LIMS_TASK_key="2C2CB8ED-6D69-457C-981C-8C7CFC24A3E7"

#SequencingMachine = "NextSeqEX"
#RunID = "190208_NB501376_0002_TQZAEJS3XT"
#SampleID = ""

f = open("/data/Tools/bin/RunFastqc_API_manual.txt", 'r')
lsSample_info = f.readlines()
for i in range(0, len(lsSample_info)) : 
	lsSample_info[i] = lsSample_info[i].strip().split("\t")
	print(lsSample_info[i])

def RunFastQC(SequencingMachine, RunID, SampleID):

        #SequencingMachine, RunID = SampleInfo(SampleID)
	
        s = requests.Session()
        headers = {"content-type" : "application/json"}
        data = [{"name":"FastQC","serial":SampleID,"argument":[SequencingMachine,RunID,SampleID,'pe'],"priority":"Immediate"}]
        TaskUrl = "http://lims.labgenomics.com:8080/lims/api/task/?key=%s" % LIMS_TASK_key
        js_data = json.dumps(data)
	print(js_data)
        s.put(TaskUrl, headers=headers, data=js_data)

	#js_url = urllib.urlopen(TaskUrl).read()
	#print(js_url)

        time.sleep(0.5)
        return 0


def main() : 
	for i in range(0, len(lsSample_info)) : 
		SequencingMachine = lsSample_info[i][0]
		RunID = lsSample_info[i][1]
		SampleID = lsSample_info[i][2]
		RunFastQC(SequencingMachine, RunID, SampleID)


main()
