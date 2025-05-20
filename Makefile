DATASET := $(realpath $(HOME)/Documents/datasets/hlsBench)

TARGET_DIR := $(DATASET)/dsp/fir

run: clean
	python3 src/main.py --algo_path $(TARGET_DIR)

clean:
	-rm -rf target hlsProj hlsOptProj vitis_hls.log
	-rm -rf impl/*
	-rm -rf ref/*
	-rm -rf hls/*
