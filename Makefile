DATASET := $(realpath $(HOME)/Documents/datasets/hlsBench/data)
DEFAULT := $(DATASET)/dsp/fir

DATASET_RA := $(realpath $(HOME)/Documents/workspace/exp/bitwidth_replace/build/ra/gpt-4o)
DEFAULT_RA := $(DATASET_RA)/fir

BUILD := $(abspath ./build)
OUT := $(abspath ./out)
RESULT := $(abspath ./result.txt)

ALL := $(shell find $(DATASET) -mindepth 2 -maxdepth 2 -type d)

default: clean
	python3 src/main.py --algo_path $(DEFAULT)

opt: clean
	python3 src/main.py --type opt --algo_path $(DEFAULT_RA)

run: $(ALL)
	-rm -rf $(OUT)
	-mkdir -p $(OUT)
	@for d in $^; do \
		rm -rf $(BUILD); \
		echo "==> Generate for $$d"; \
		python3 src/main.py --algo_path $$d; \
	done

runGen: $(ALL)
	-rm -rf $(OUT)
	-rm -f $(RESULT)
	-mkdir -p $(OUT)
	@script/generate.sh $^

clean:
	-rm -rf $(BUILD)
	-rm -rf $(RESULT)
	-rm -rf vitis_hls.log

count:
	find src -type f -name "*.py" | xargs wc -l

.PHONY: default run clean
