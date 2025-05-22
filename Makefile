DATASET := $(realpath $(HOME)/Documents/datasets/hlsBench/data)
DEFAULT_DIR := $(DATASET)/dsp/fir

BUILD_DIR := $(abspath ./build)

ALL := $(shell find $(DATASET) -mindepth 2 -maxdepth 2 -type d)

# 1. find all second-level directories
# 2. traverse all directories
# 3. for each directories, do the run target

default: clean
	python3 src/main.py --algo_path $(DEFAULT_DIR)

run: $(ALL)
	@for d in $^; do \
		-rm -rf $(BUILD_DIR); \
		-rm vitis_hls.log; \
		echo "==> Generate for $$d"; \
		python3 src/main.py --algo_path $$d; \
	done

clean:
	-rm -rf $(BUILD_DIR)
	-rm -rf hlsProj hlsOptProj vitis_hls.log
	-rm -rf hls/*

.PHONY: default run clean
