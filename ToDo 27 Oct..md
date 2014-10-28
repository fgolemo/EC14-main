This will affect the pop:
* Density 
* Lifetime (relates to density)
* Fertility distance
* How often they can procreate

Meeting Notes:
* **We need to see what the arena size values mean**
* Assign a scale to the individuals and their walking distance
* Assign weights to find size, to be able to tell where and how big the robots are in the arena
* i.e. the robot covers so and so much of the arena in its lifetime - to be able to set the pop size
* We need to make sure r.o.b. == r.o.d.

* Snapshot the traces (visually) to be able to see the density and how they move.
* This will give us a feel for what parameters we need to play with.
* We need to get a more or less stable population size.
* We could qsub the main script and use its own home dir

### Separate Visualisation Project
* Trace visualisation
* GNU plots
* Plot showing for a given time slice, where the new individuals are mated (eventually this could be animated)
* Plot of the population size over time (count how many individuals are in a time step?)

### Paper start
* Describe how the system works
* IMP: We are simulating them separately, there is no real interaction -BUT this is still a good model to evaluate evolutionary alg.
* We cant put obstacles (or can we?)

#### Goals:
* Stable population params
* Nick Cheney's distance val. can be set as the upper bound

## Next Meeting 3rd Nov @ 1PM

