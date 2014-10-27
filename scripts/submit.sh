#!/bin/sh
module load stopos
stopos create -p ~/dead.${2}.pool
stopos add -p ~/dead.${2}.pool $1

scriptdir=${HOME}/EC14-main/scripts

JOB_ID=`qsub -o logs -e logs -v pool=~/dead.${2}.pool ${scriptdir}/run_vox.sh`

#display job queue
showq -u $USER
