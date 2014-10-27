vcmain
======

Control script for the experiments of the Evolutionary Computing 2014 group, controlling HyperNEAT and Voxelyze workers on the Lisa.surfsara cluster.

### Main Script

When run, `EC14-main.py` asks for user input to specify:

* Is the experiment a continuation of a previous experiment?
  * If so, where are the files located (specify path)?
  * If not, what should the experiment be named (this defines the directory as ~/EC14-Exp-**input**)?
    * What is the desired population size (`pop_size`)?
* What are the database parameters for the experiment database (a mysql database must already exist)?
* What is the desired individual max age?
* What is the desired experiment max time?
* Should the population have a randomized birth time?
  *If so, what is the time window for the births (earliest and latest birth time)?
* What type of arena should be implemented (bouncy or infinite)?


The script then runs creates `pop_size` number of individual IDs in the database and marks them as *not yet hyperneated* (one individual per row). This will be picked up by the HyperNEAT worker and will generate the initial population.

The script also copies a version of itself into the experiment directory, along with copies of `hyperneat_worker.py`, `voxelyze_worker.py`,`db.py`, and the other HyperNEAT and VoxCad scripts which are not in this repo. It also saves a `config.ini` file with the experiment configuration.

The script then spawns the two workers which run on the home node constantly, checking for new todos.

### Hyperneat Worker

The HyperNEAT worker is launched and begins parsing the database for IDs that have not yet been processed. When it finds such an individual, it passes its ID and the corresponding parameters to HyperNEAT (if the individual has 0 parents, it needs to be generated randomly, if it has 1 parent, it needs to be mutated, and if it has 2 parents, it needs to be parented). HyperNEAT saves an `.xml` and a `.vxa` file in its directory. The files are named after the current experiment name and their Individual ID.

### Voxelyze Worker

The Voxelyze worker checks the database iteratively, to find individuals which have been generated, but not yet virtualizes. When it finds such an individual, it adds its ID to a .pool file, until the pool contains 12 individuals. When the threshold is reached, the worker submits the pool to Lisa via **stopos**.

### Preprocessing

**#TODO**


#### Usage of the HN Dummy

`python HyperNEATdummy.py -I test.dat -O IamAchildID -ORG parent1 parent2`

where

* `test.dat` is the parameter file
* `IamAchildID` is the filename prefix of the child to be created
* `parent1` (optional) for mutation, id of the parent
* `parent2` (optional), together with parent1 for offspring
 
...generates 2 files in the same directory: `IamAchildID-genotype.xml` and `IamAchildID-vox.vxa`. Both should be moved elsewhere.

