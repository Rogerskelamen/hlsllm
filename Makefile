TEST_FILE := "./input/buble_sort.txt"

run: clean
	@python3 src/main.py --algo_file $(TEST_FILE)

clean:
	-rm -rf hlsProj vitis_hls.log
	-rm -rf impl/*
	-rm -rf ref/*
	-rm -rf hls/*
