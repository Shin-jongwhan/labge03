#!/usr/bin/python

#python GenerationTask.py Runid Sampleid
#ex) python GenerationTask.py 161128_NB501509_0144_AH75NFBGXY 2016112206227-EF2-HT

import requests
import json,urllib
from subprocess import PIPE,Popen
import os, sys, random, argparse


# 0. Set the parameters and help
#@parser = argparse.ArgumentParser(description="This script execute REST api (Labgenomcis LIMS)",
#         formatter_class=argparse.ArgumentDefaultsHelpFormatter)
#parser.add_argument('-Pipeline', type=str, help="Analysis Pipeline")
#parser.add_argument('-Serial', type=str, help="Serial")
#parser.add_argument('-Parameter_File',   type=str, help="Parameter file...")
#args = parser.parse_args()

# API Key
LIMS_TASK_key="2C2CB8ED-6D69-457C-981C-8C7CFC24A3E7"


def main(argv):
        s = requests.Session()
        headers = {"content-type" : "application/json"}
        data = [{"name":"FastQC","serial":sys.argv[3],"argument":[sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4]],"priority":"Start"}]
        TaskUrl = "http://lims.labgenomics.com:8080/lims/api/task/?key=%s" % LIMS_TASK_key
        js_data = json.dumps(data)
        s.put(TaskUrl, headers=headers, data=js_data)


if __name__ == "__main__":
        main(sys.argv[1:])

