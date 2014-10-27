#!/bin/sh

pool=dead${2}.pool
exp=${3}

module load stopos
stopos create -p ${pool}
stopos add -p ${pool} $1

scriptdir=${HOME}/EC14-main/scripts

JOB_ID=`qsub -o ${2}.output.log -e ${2}.error.log -l nodes=1,walltime=600 -v pool=${pool},exp=${exp} ${scriptdir}/run_vox.sh`

#display job queue
showq -u $USER
