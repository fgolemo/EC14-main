vcmain
======

Control script for the experiments of the Evolutionary Computing 2014 group, controlling HyperNEAT and Voxelyze workers on the Lisa.surfsara cluster.


**Usage of the HN Dummy**

`python HyperNEATdummy.py -I test.dat -O IamAchildID -ORG parent1 parent2`

where

* `test.dat` is the parameter file
* `IamAchildID` is the filename prefix of the child to be created
* `parent1` (optional) for mutation, id of the parent
* `parent2` (optional), together with parent1 for offspring