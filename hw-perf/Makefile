CC=gcc
OPT=-Wall -march=native
TIME=/usr/bin/time -p
BUILD_DIR=build

casperf8:
	$(CC) $(OPT) -o $(BUILD_DIR)/casperf8 casperf8.c
casperf8uncontended:
	$(CC) $(OPT) -o $(BUILD_DIR)/casperf8uncontended casperf8uncontended.c
casperf64:
	$(CC) $(OPT) -o $(BUILD_DIR)/casperf64 casperf64.c
casperf32:
	$(CC) $(OPT) -o $(BUILD_DIR)/casperf32 casperf32.c
casperf16:
	$(CC) $(OPT) -o $(BUILD_DIR)/casperf16 casperf16.c
casperf64multiline:
	$(CC) $(OPT) -o $(BUILD_DIR)/casperf64multiline casperf64multiline.c
casperf128:
	$(CC) $(OPT) -o $(BUILD_DIR)/casperf128 casperf128.c
casperf8contended:
	$(CC) $(OPT) -o $(BUILD_DIR)/casperf8contended casperf8contended.c
cache:
	$(CC) $(OPT) -o $(BUILD_DIR)/cache cache.c

time_casperf8:
	$(TIME) ./$(BUILD_DIR)/casperf8
time_casperf8uncontended:
	$(TIME) ./$(BUILD_DIR)/casperf8uncontended
time_casperf64:
	$(TIME) ./$(BUILD_DIR)/casperf64
time_casperf32:
	$(TIME) ./$(BUILD_DIR)/casperf32
time_casperf16:
	$(TIME) ./$(BUILD_DIR)/casperf16
time_casperf64multiline:
	$(TIME) ./$(BUILD_DIR)/casperf64multiline
time_casperf128:
	$(TIME) ./$(BUILD_DIR)/casperf128
time_casperf8contended:
	$(TIME) ./$(BUILD_DIR)/casperf8contended
run-cache:
	./$(BUILD_DIR)/cache

.PHONY: build-all time-all all clean
build-all: casperf8 casperf8uncontended casperf64 casperf32 casperf16 casperf64multiline casperf128 casperf8contended cache

time-all: time_casperf8 time_casperf8uncontended time_casperf64 time_casperf32 time_casperf16 time_casperf64multiline time_casperf128 time_casperf8contended

all: build-all time-all run-cache

clean:
	rm -f $(BUILD_DIR)/*
