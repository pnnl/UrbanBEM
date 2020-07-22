
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

# json target - only the first case since the script only needs to be run once
$(JSON_DIR)/cbecs1.json: ../input/cbecs-standardized-200715.xlsx
	python standard_excel_processor.py

# individual IDF target
$(IDF_DIR)/%.idf: $(JSON_DIR)/%.json
	mkdir -p ../ep_input/input &&
	mkdir -p ../ep_input/stdout &&
	mkdir -p ../ep_input/stderr &&
	srun1 -A urbanbem singularity exec -B .. openstudio_python.sif python json2idf.py $(basename $(notdir $<))

# individual output target
$(OUT_DIR)/%.meter.csv: $(IDF_DIR)/%.idf
	mkdir -p ../ep_output/output &&
	mkdir -p ../ep_output/stdout &&
	mkdir -p ../ep_output/stderr &&
	srun1 -A urbanbem python simulate.py $(basename $(notdir $<))

# output targets
output: $(addprefix $(OUT_DIR)/,$(OUT_FILES))

# idfs target
idfs: $(addprefix $(IDF_DIR)/,$(IDF_FILES))

# conversion target
conversion:
	$(MAKE) -k -j 240 idfs
	
# all target
simulate:
	$(MAKE) -k -j 240 output

# clean IDF targets - to be done after scripts are edited
cleanIDF:
	rm ../ep_input/input/*
	
cleanOutput:
	rm ../ep_output/output/*
