import os
import csv
from dataclasses import dataclass

@dataclass
class Stage:
    start: int
    idx: int
    name: str

@dataclass
class Retire:
    cycle: int
    idx: int

# Helper function to increase filename
def increment_filename(filename):

    new_idx = int(filename[-8:-4])+1
    if new_idx > 9999:
        return None
    new_filename = filename[:-8] + f"{new_idx:04d}" + ".txt"

    if os.path.exists(new_filename):
        return new_filename
    else:
        return None

class konata_converter(object):

    def __init__(self):
        self.timing_filename = ""
        self.output_filename = ""
        self.asmtrace_filename = ""

        self.timing_file = None
        self.output_file = None
        self.asmtrace_file = None

        self.asmcontent = None
        self.asmtrace_line = 0

        self.firstIdx = 0

        # stage mapping: CSV header
        self.first_stage = "IF_stage"
        self.stage_mapping = {}

    # open all initail file handlers
    def setup(self, timing_filename, output_filename = None, asmtrace_filename = None):
        
        if int(timing_filename[-8:-4]) > 0:
            for i in range(int(timing_filename[-8:-4])):
                temp_filename = timing_filename[:-8] + f"{i:04d}" + ".csv"
                try:
                    with open(temp_filename, 'r') as f:
                        num_lines = sum(1 for _ in f)
                        self.firstIdx = self.firstIdx + num_lines - 1
                    # print(f"{temp_filename}: {num_lines} lines")
                except FileNotFoundError:
                    print(f"{temp_filename}: File not found")

        self.timing_filename = timing_filename
        self.timing_file = open(timing_filename, newline='')
        
        self.reader = csv.DictReader(self.timing_file)
        self.first_stage = self.reader.fieldnames[0]
        self.first_stage_short = self.first_stage.split('_')[0]


        if output_filename is not None:
            self.output_filename = output_filename
            self.output_file = open(output_filename, 'w')
        else:
            self.output_filename = "pipeline_output.trace"
            self.output_file = open("pipeline_output.trace", "w")

        if asmtrace_filename is not None:

            # always start at index 0 for asm trace files
            if int(asmtrace_filename[-8:-4]) > 0:
                asmtrace_filename = asmtrace_filename[:-8] + "0000.txt"

            self.asmtrace_filename = asmtrace_filename
            self.asmtrace_file = open(asmtrace_filename, 'r')
            self.asmcontent = self.asmtrace_file.readlines()


    # close all file handlers
    def close(self):

        if self.timing_file is not None:
            self.timing_file.close()

        if self.output_file is not None:
            self.output_file.close()

        if self.asmtrace_file is not None:
            self.asmtrace_file.close()

    # helper function to write at each new cycle
    def konata_next_cycle(self):
        self.output_file.write(f"C\t1\n")

    # helper function to write when a new stage starts
    def konata_stage_write(self, stage):

        while self.asmcontent is not None and stage.idx+1 >= self.asmtrace_line+len(self.asmcontent):
            old_length = len(self.asmcontent)-1
            self.asmtrace_filename = increment_filename(self.asmtrace_filename)

            if self.asmtrace_filename is not None:
                self.asmtrace_file.close()
                self.asmtrace_line = self.asmtrace_line + old_length
                self.asmtrace_file = open(self.asmtrace_filename, 'r')
                self.asmcontent = self.asmtrace_file.readlines()

            else:
                self.asmcontent = None

        if stage.name == self.first_stage_short:
            self.output_file.write(f"I\t{stage.idx}\t{0}\t{0}\n")
            
            if self.asmcontent is not None:
                self.output_file.write(f"L\t{stage.idx}\t{0}\t{self.asmcontent[stage.idx+1-self.asmtrace_line]}\n")
            else:
                self.output_file.write(f"L\t{stage.idx}\t{0}\ttiming_line_{stage.idx}\n")

        self.output_file.write(f"S\t{stage.idx}\t{0}\t{stage.name}\n")

    # helper function to write retired instructions
    def konata_retire_write(self, retire):
        self.output_file.write(f"R\t{retire.idx}\t{retire.idx}\t{0}\n")


    # main logic to transform timing files into konata readable files
    def convert(self):

        prev_written_cycle = 0
        min_cycle = 0

        stages = []
        retire_points = []

        for i, row in enumerate(self.reader):
            
            if i == 0:
                stage_mapping = {col: col.split("_")[0] for col in row}
                print(stage_mapping)
                self.output_file.write(f"Kanata\t0004\n")
                prev_written_cycle = int(row[self.first_stage]) - 1

            cycles = []
            fetchcycle = int(row[self.first_stage])
            
            for csv_stage, output_stage in stage_mapping.items():
                cycle = int(row[csv_stage])
                if cycle > fetchcycle or csv_stage==self.first_stage:
                    
                    # find cycle less than or equal
                    less_than = [x for x in cycles if x <= cycle]
                    cycles.append(cycle)

                    if len(less_than) > 0:
                        stages.append(Stage(max(less_than), i + self.firstIdx, output_stage))
                    else:
                        stages.append(Stage(cycle-1, i + self.firstIdx, output_stage))

            min_cycle = min(cycles)-1
            retire_points.append(Retire(max(cycles), i + self.firstIdx))

            while prev_written_cycle < min_cycle:
                #print(min_cycle)
                if prev_written_cycle > 0:
                    self.konata_next_cycle()

                j = 0
                while j < len(stages):
                    stage = stages[j]
                    if stage.start == prev_written_cycle:
                        self.konata_stage_write(stage)
                        del stages[j]
                    else:
                        j += 1
                
                j = 0
                while j < len(retire_points):
                    retire = retire_points[j]
                    if retire.cycle == prev_written_cycle:
                        self.konata_retire_write(retire)
                        del retire_points[j]
                    else:
                        j += 1

                prev_written_cycle += 1

        
        # Write all remaining cycles
        while len(stages) > 0 or len(retire_points) > 0:
            self.konata_next_cycle()

            j = 0
            while j < len(stages):
                stage = stages[j]
                if stage.start == prev_written_cycle:
                    self.konata_stage_write(stage)
                    del stages[j]
                else:
                    j += 1
            
            j = 0
            while j < len(retire_points):
                retire = retire_points[j]
                if retire.cycle == prev_written_cycle:
                    self.konata_retire_write(retire)
                    del retire_points[j]
                else:
                    j += 1

            prev_written_cycle += 1

        # Prints "stages" or "retired_points" if there exist not processed entities
        for stage in stages:
            print(stage)
        for retire in retire_points:
            print(retire)

        print(f"Pipeline trace written to '{self.output_filename}' in Kanata/Gem5-O3PipeView format.")