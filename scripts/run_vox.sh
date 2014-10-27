#!/bin/sh
module load stopos

voxdir=~/EC14-voxelyze/voxelyzeMain
cd $voxdir

ncores=`sara-get-num-cores`

for ((i=1; i<=ncores; i++)) ; do
  stopos next -p ${pool}
  if [ "$STOPOS_RC" != "OK" ] ; then
      break
    fi
  $STOPOS_VALUE
  stopos remove -p ${pool}
done
