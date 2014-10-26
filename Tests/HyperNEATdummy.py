# HyperNEAT dummy
import sys

if (len(sys.argv) < 7):
	print("Error, need the parameters: -I parameters.dat -R $RANDOM -O targetID -ORG [parent1 [parent2]]")
	exit()

id = sys.argv[6]
genotypeFile = id + "-genotype.xml"
voxFile = id + "-vox.vxa"
print("here HN will print random strings\nline by line\ncontaining some debugging infos")

print("generating 2 files:\n"+genotypeFile+" & "+voxFile)

fileG = open(genotypeFile, "w")
fileG.write("HyperNEAT dummy genotype XML file\n")
fileG.close()

fileV = open(voxFile, "w")
fileV.write("HyperNEAT dummy Voxelyze VXA file\n")
fileV.close()

print("done")