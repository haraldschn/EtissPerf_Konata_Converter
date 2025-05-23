example_rv32_4issue:
	python main.py ./examples/crc32_RV32_4ISSUE/RV32_4ISSUE_timing_0000.csv \
		-a ./examples/crc32_RV32_4ISSUE/asm_trace_0000.txt \
		-o ./pipeline_trace_rv32_4issue.trace

example_CVA6:
	python main.py ./examples/ud_CVA6/CVA6_timing_0000.csv \
		-a ./examples/ud_CVA6/asm_trace_0000.txt \
		-o ./pipeline_trace_cva6.trace

example_CV32E40P:
	python main.py ./examples/crc32_CV32E40P/CV32E40P_timing_0000.csv \
		-a ./examples/crc32_CV32E40P/asm_trace_0000.txt \
		-o ./pipeline_trace_cv32e40p.trace