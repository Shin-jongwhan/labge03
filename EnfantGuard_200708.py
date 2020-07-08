#!/usr/bin/python

import os, sys, random, argparse, requests
import json,urllib

#sys.argv.remove(sys.argv[1])

#print sys.argv[2]
#0. Set the parameters and help
#parser = argparse.ArgumentParser(description="Sequencing Observer", formatter_class=argparse.ArgumentDefaultsHelpFormatter)

#parser.add_argument('-N', type=str, choices=['NextSeq01', 'NextSeq02', 'NextSeq03' ], required=True, help="Device Name")
#args = parser.parse_args()

LIMS_TASK_key="2C2CB8ED-6D69-457C-981C-8C7CFC24A3E7"


def main(argv):
        s = requests.Session()
        headers = {"content-type" : "application/json"}
	# argv[10] Device (ex) NextSeq01)
	# priority : Start, Immediate, High, Above Normal, Normal, Below Normal, Low
        data = [{"name":"EnfantGuard","serial":sys.argv[2],"argument":[sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6],sys.argv[7],sys.argv[8],sys.argv[9],sys.argv[10]],"priority":"high"}]
        TaskUrl = "http://lims.labgenomics.com:8080/lims/api/task/?key=%s" % LIMS_TASK_key
        js_data = json.dumps(data)
        s.put(TaskUrl, headers=headers, data=js_data)


if __name__ == "__main__":
        main(sys.argv[1:])


