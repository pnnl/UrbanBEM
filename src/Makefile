
# in case make is run with no arguments
nothing:
	@ echo "No action performed...(you must give an explicit makefile target)"
	
# definitions
IDF_DIR := ../ep_input/input
JSON_DIR := ../input/std_json_raw
OUT_DIR := ../ep_output/output
JSON_FILES := $(notdir $(wildcard $(JSON_DIR)/*.json))
IDF_FILES := $(subst json,idf,$(JSON_FILES))
OUT_FILES := $(subst idf,meter.csv,$(IDF_FILES))

# individual IDF target
$(IDF_DIR)/%.idf: $(JSON_DIR)/%.json
	srun1 -A urbanbem singularity exec -B .. openstudio_python.sif python json2idf.py $(basename $(notdir $<))

# individual output target
$(OUT_DIR)/%.meter.csv: $(IDF_DIR)/%.idf
	srun1 -A urbanbem python simulate.py $(basename $(notdir $<))
	
# set IDFs as secondary targets so make doesn't automatically remove them
.SECONDARY: $(addprefix $(IDF_DIR)/,$(IDF_FILES))

# output targets
output: $(addprefix $(OUT_DIR)/,$(OUT_FILES))
	
# all target
simulate:
	mkdir -p ../ep_input/input && \
	mkdir -p ../ep_input/stdout && \
	mkdir -p ../ep_input/stderr && \
	mkdir -p ../ep_output/output && \
	mkdir -p ../ep_output/stdout && \
	mkdir -p ../ep_output/stderr && \
	mkdir -p ../hvac_dev && \
	mkdir -p ../swh_dev && \
	$(MAKE) -k -j 288 output

# clean IDF targets - to be done after scripts are edited
cleanJSON:
	rm ../input/std_json_raw/*

# clean IDF targets - to be done after scripts are edited
cleanIDF:
	rm -rf ../ep_input

# clean IDF targets - to be done after scripts are edited
cleanOutput:
	rm -rf ../ep_output
