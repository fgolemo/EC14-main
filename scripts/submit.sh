module load stopos
stopos create -p dead.pool
stopos add -p dead.pool $1

workdir=${HOME}/EC14-main/scripts

JOB_ID=`qsub -o logs -e logs -t ${workdir}/run_vox.sh`

#display job queue
showq -u $USER
