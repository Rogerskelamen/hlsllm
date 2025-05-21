DATASET := $(realpath $(HOME)/Documents/datasets/hlsBench)

BUILD := $(abspath ./build)

TARGET_DIR := $(DATASET)/dsp/fir

run: clean
	python3 src/main.py --algo_path $(TARGET_DIR)

clean:
	-rm -rf $(BUILD)
	-rm -rf hlsProj hlsOptProj vitis_hls.log
	-rm -rf hls/*
