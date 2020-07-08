#################################################################################
#										#
# This script will generate run task into corelims only				#
#										#
#################################################################################

runid=${1}
Demulti_device=${2}


echo Generate run task into corelims...
echo python /data/Tools/bin/ReDemulti_corelims.py ReDemulti $runid $Demulti_device SampleSheet.csv
python /data/Tools/bin/ReDemulti_corelims.py ReDemulti $runid $Demulti_device SampleSheet.csv

