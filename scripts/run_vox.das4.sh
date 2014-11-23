#!/bin/sh

voxdir=${HOME}/EC14-voxelyze/voxelyzeMain
cd $voxdir

mkdir "$TMPDIR"/vox

#!/bin/bash
while read line; do
(
    ./voxelyze -f ${population}${line}_vox.vxa -p 100 > "$TMPDIR"/vox/${line}.trace
    mv "$TMPDIR"/vox/${line}.trace ${traces}afterVox/${line}.trace
    echo "trace ${line} done"
) &
done < ${pool}

wait
echo "done"