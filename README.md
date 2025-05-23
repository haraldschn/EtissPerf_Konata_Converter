# EtissPerf Konata Converter
## Description

This Python script allows converting `*_timing_<ID>.csv` timing files generated with the Etiss-based Performance estimator into Onikiri2-Kanata/Gem5-O3PipeView files, readable by the Konata instruction pipeline visualizer. Using the additionally generated assembly traces `asm_trace_<ID>.txt` allows labeling the lines with their appropriate assembly instruction.

- Timing file examples were generated with [PerformanceSimulation_workspace](https://github.com/tum-ei-eda/PerformanceSimulation_workspace).
- Konata instruction pipeline visualizer [Konata](https://github.com/shioyadan/Konata).


## Usage

Simple usage examples can be found in the `Makefile`.

To convert timing files simply call `python main.py <TIMING FILE>`

The following arguments are optional:
- `-a` ... input path of assembly trace
- `-o` ... output path (defaults to `./pipeline_output.trace` if not used)


## Simplifications 

To allow for a simple implementation following simplifications were considered.

- Because the start time of the first stage is unknown from the timing files. The first stage takes (for each line) the instructions minimum time minus 1 as its start time.
- For timing file input, with an index greater than 0, all the files with a lower index are needed to calculate the correct trace/line index. (Needed to sync with assembly trace).
 (eg. inputting timing file `CVA6_timing_0002.csv` would need to have `CVA6_timing_0000.csv` and `CVA6_timing_0001.csv` present in its source folder)
- All of the file indices are simply taken by index slicing [-8:-4] of the inputted strings of the file paths. Changing the naming scheme (of either timing/assembly files) breaks extracting this indices from the filename path.