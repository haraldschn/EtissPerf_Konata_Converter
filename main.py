import argparse

from konata_converter import konata_converter

#
# The entry point of this program.
#
if __name__ == '__main__':

    # Initialize argument parser
    parser = argparse.ArgumentParser()

    # Adding optional argument
    parser.add_argument('timingfile')
    parser.add_argument("-o", "--output", help = "Set output filename/-path (default = pipeline_output.trace)")
    parser.add_argument("-a", "--asm", help = "Set (intial) assembly trace filename/-path")

    # Read arguments from command line
    args = parser.parse_args()

    print("Generating konata file for: % s" % args.timingfile)

    converter = konata_converter()

    converter.setup(args.timingfile, args.output, args.asm)
    converter.convert()
    converter.close()


