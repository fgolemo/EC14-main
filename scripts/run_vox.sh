#!/bin/sh
module load stopos

voxdir=~/EC14-voxelyze/voxelyzeMain
cd $voxdir

ncores=`sara-get-num-cores`

for ((i=1; i<=ncores; i++)) ; do
(
    stopos next -p ${pool}
    if [ "$STOPOS_RC" != "OK" ]; then # Parameter pool exhausted: we're done
        break
    fi
    ./voxelyze -f ${exp}${STOPOS_VALUE}_vox.vxa -p 100 > ${exp}${STOPOS_VALUE}.trace
    stopos remove -p ${pool}
) &
done

wait