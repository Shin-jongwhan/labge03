#!/usr/bin/env python

import os, sys, glob, subprocess, shutil, argparse, requests, json, urllib, pprint, time
from datetime import datetime as Datetime

#################################################################################
#										#
# Use only for generating run task into corelims				#
# 1. python [this_file] ReDemulti [Run_ID] [Demulti_divice] SampleSheet.csv 	#
#										#
#################################################################################
sFile_itself = os.path.abspath( __file__ ).split("/")[-1]
print("Usage : python {0} ReDemulti [Run_ID] SampleSheet.csv".format(sFile_itself))
print("This script will generate run task into corelims only")

parser = argparse.ArgumentParser()

subparser = parser.add_subparsers(help='Desired action to perform', dest='action')

parent_parser = argparse.ArgumentParser(add_help=False)

parser_ReDemulti = subparser.add_parser("ReDemulti", parents=[parent_parser], help='Re Demultiplexing')
parser_ReDemulti.add_argument("RunID", help='Only require one runID which have [Samplesheet.csv]')
parser_ReDemulti.add_argument("Demulti_device", help='Demulti_device folder in /data/Demultiplexing/')
parser_ReDemulti.add_argument("SampleSheet", help='which has new demulti sample list')

args = parser.parse_args()

LIMS_TASK_key="2C2CB8ED-6D69-457C-981C-8C7CFC24A3E7"

Machinelist = {'NS500759':'NextSeq01','NS500435':'NextSeq02','NB501509':'NextSeq03','NDX550181':'NextSeqDx','M01849':'MiSeq01','M03183':'MiSeq02','M70503':'MiSeqDx01',}
dicSequencing_Device = {'NextSeq01' : 'NextSeq_01', 'NextSeq02' : 'NextSeq_02', 'NextSeq03' : 'NextSeq_03', 'NextSeqDx' : 'NextSeqDx_01', 'NextSeqEX' : 'NextSeq_EX', 'MiSeq01' : 'MiSeq_01', 'MiSeq02' : 'MiSeq_02', 'MiSeq03' : 'MiSeq_03', 'MiSeqEX' : 'MiSeq_EX'}

def SampleInfo(SampleID):
        SampleID = SampleID.replace('-Merged','')

        try :
                RunDir = glob.glob('/Demultiplexing/*/*/'+SampleID+'_*')[-1]
                RunID = RunDir.split('/')[-2]           # find RunID if there is SampleID in the RunID

        except :
                try :
                        RunDir = glob.glob('/Demultiplexing/Analysis/Project/EnfantGuard/*/'+SampleID)[-1]
                        RunID = RunDir.split('/')[-2]

                except :
                        print('can\'t find '+SampleID+' file in Demultiplexing Directory')
                        exit()

        MachineID = RunID.split("_")[1]
        SequencingMachine = Machinelist[MachineID]
        print(SequencingMachine+"\t"+RunID+"\t"+SampleID)
        return SequencingMachine, RunID


def RunFastQC(SampleID):
        SequencingMachine, RunID = SampleInfo(SampleID)

        s = requests.Session()
        headers = {"content-type" : "application/json"}
        data = [{"name":"FastQC","serial":SampleID,"argument":[SequencingMachine,RunID,SampleID,'pe'],"priority":"Immediate"}]
        TaskUrl = "http://lims.labgenomics.com:8080/lims/api/task/?key=%s" % LIMS_TASK_key
        js_data = json.dumps(data)
        s.put(TaskUrl, headers=headers, data=js_data)

        time.sleep(0.5)
        return 0


def SampleList(RunDir, SampleSheet) :
        # find which SampleID have to be re-analyzed.
        SampleIDList = []

        try :
                NewSampleSheet = open(RunDir+'/{0}'.format(SampleSheet))
        except OSError :
                print('can\'t find '+RunDir+'/{0} file'.format(SampleSheet))
                exit()
        else :
                SampleSheetFlag = 0
                SampleIDList = []

                with NewSampleSheet :
                        for line in NewSampleSheet :
                                if SampleSheetFlag == 1:
                                        linesp = line.strip().split(',')
                                        SampleIDList.append(linesp[0])
                                if line.startswith('Sample_ID'):
                                        SampleSheetFlag = 1
        return SampleIDList


def ReDemulti(RunID, Demulti_device, SampleSheet):

	# find run path and sequencing machine which were used.
	sSequencing_device = dicSequencing_Device[Demulti_device]
	#print(glob.glob('/data/Instrument/*/'+RunID))
	RunDir = '/data/Instrument/{0}/{1}'.format(sSequencing_device, RunID)
	Demulti_run_dir = "/data/Demultiplexing/{0}/{1}".format(Demulti_device, RunID)
	if os.path.isdir(RunDir) != True : 
		print("Please check run directory : {0}".format(RunDir))
		sys.exit()
	else : 
		print("Run directory : {0}".format(RunDir))
	if os.path.isdir(Demulti_run_dir) != True : 
		print("Don't exist demulti directory : {0}".format(Demulti_run_dir))
	else : 
		print("Demultiplexing directory : {0}".format(Demulti_run_dir))
	if os.path.isfile(RunDir + "/Cancel.txt") == True : 
		os.system("rm {0}/Cancel.txt".format(RunDir))
		
	if SampleSheet == "SampleSheet.csv" : 
		print("SampleSheet.csv : default")
		print("Remove original fastq file and folder /data/Demultiplexing/{0}/{1}".format(Demulti_device, RunID))
		sRM_demulti_folder_CMD = "rm -r {0}".format(Demulti_run_dir)
		if os.path.isdir(Demulti_run_dir) == True : 
			os.system(sRM_demulti_folder_CMD)
		#for SampleID_fastq in glob.glob('/Demultiplexing/'+Demulti_device+'/'+RunID+'/'+'*.fastq.gz') :
		#	print("remove fastq {0}".format(SampleID_fastq))
		#	os.remove(SampleID_fastq)
	
		sRM_RTAComplete_CMD = "rm {0}/RTAComplete.txt".format(RunDir)
		sRename_sampleSheet_CMD = "rename SampleSheet.csv SampleSheet_old.csv {0}/SampleSheet.csv".format(RunDir)
		print(sRM_RTAComplete_CMD)
		os.system(sRM_RTAComplete_CMD)
		time.sleep(1)
		print(sRename_sampleSheet_CMD)
		os.system(sRename_sampleSheet_CMD)
		time.sleep(1)
		
		sMV_Run_dir_CMD_1 = "mv {0} /data/Instrument/".format(RunDir)
		sMV_Run_dir_CMD_2 = "mv /data/Instrument/{0} {1}/".format(RunID, "/".join(RunDir.split("/")[:-1]))
		print("move {0} to /data/Instrument/".format(RunDir))
		os.system(sMV_Run_dir_CMD_1)
		time.sleep(5)
		print("move /data/Instrument/{0} to {1}/".format(RunID, "/".join(RunDir.split("/")[:-1])))
		os.system(sMV_Run_dir_CMD_2)
		#time.sleep(5)
	

def main():

	if args.action == 'ReDemulti' :
		RunID = args.RunID
		Demulti_device = args.Demulti_device
		SampleSheet = args.SampleSheet
		ReDemulti(RunID, Demulti_device, SampleSheet)


main()
