
# In case make is run with no arguments
nothing:
	@ echo "No action performed...(you must give an explicit makefile target)"
	
# Definitions
OUT_DIR := ../ep_input/input
IN_DIR := ../input/std_json_raw
IN_FILES := $(notdir $(wildcard $(IN_DIR)/*.json))
OUT_FILES := $(subst json,idf,$(IN_FILES))

# Individual IDF target
$(OUT_DIR)/%.idf: $(IN_DIR)/%.json
	srun -A urbanbem singularity exec -B .. openstudio_python.sif python json2idf.py $(basename $(notdir $<))

# IDF targets
ep_input: $(addprefix $(OUT_DIR)/,$(OUT_FILES))
	
# all target
all:
	$(MAKE) -k -j 240 ep_input

# clean targets - to be done after scripts are edited
clean:
	rm ../ep_input/input/* && rm ../ep_input/stdout/* && rm ../ep_input/stderr/*
	
test:
	srun -A urbanbem singularity exec -B .. openstudio_python.sif python json2idf.py cbecs1
