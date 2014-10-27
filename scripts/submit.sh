#!/bin/sh

# arg 1 has to be of format EC14-Exp-15 where 15 is the id of the experiment
# arg 2 is the number of the pool to use. The corresponding pool file has to be found at ${HOME}/${1}/pool/vox.${2}.pool

base=${HOME}/${1}

pool=dead${2}.pool
population=/${1}/population #have to skip home, because qsub replaces it
pool_input=${base}/pool/vox.${2}.pool

module load stopos
stopos create -p ${pool}
stopos add -p ${pool} ${pool_input}

scriptdir=${HOME}/EC14-main/scripts

JOB_ID=`qsub -o ${2}.output.log -e ${2}.error.log -l nodes=1,walltime=600 -v pool=${pool},population=${population} ${scriptdir}/run_vox.sh`

#display job queue
showq -u $USER
