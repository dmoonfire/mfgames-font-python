import logging
import codecs
import subprocess
import os
import tempfile
import shutil

import mfgames_tools.process


class GenerateUnicodeChart(mfgames_tools.process.InputFileProcess):
    """A process that takes a single font file and generates a
    PDF-based Unicode chart."""

    def setup_arguments(self, parser):
        # Call the base implementation for common parameters.
        super(GenerateUnicodeChart, self).setup_arguments(parser)

        # Set up the required command-line options.
        parser.add_argument(
            'pdf',
            type=str,
            help="Output PDF file.")

        # Set up the additional arguments.
        parser.add_argument(
            '--start', '-s',
            type=str,
            default='0000',
            help="Hexdecimal range to start the code.")
        parser.add_argument(
            '--end', '-e',
            type=str,
            default='007F',
            help="Hexdecimal range to start the code.")

    def get_help(self):
        return "Generate a Unicode chart using XeLaTeX"

    def process_file(self, file):
        # Get the logging context.
        self.log = logging.getLogger('unicode-chart')

        # Set up a temporary directory to store everything.
        dirname = tempfile.mkdtemp(prefix='unicode-chart-')
        self.log.debug('Using temporary directory: ' + dirname)

        # Generate a XeLaTeX file that contains the chart with the
        # character ranges.
        chart_filename = os.path.join(dirname, "chart.tex")
        self.generate_chart(chart_filename)

        # Generate the PDF using XeLaTeX.
        pdf_filename = os.path.join(dirname, "chart.pdf")
        self.generate_pdf(dirname, chart_filename, pdf_filename)

        # Move the generated PDF into the output location.
        self.log.debug("Moving generated PDF to " + self.args.pdf)
        shutil.move(pdf_filename, self.args.pdf)

        # Clean up the temporary files.
        shutil.rmtree(dirname)
        self.log.debug('Cleaned up temporary directory')

    def generate_chart(self, filename):
        """Generates a Unicode chart of the given filename."""

        # Figure out the columns we'll be generating. We take the
        # first three characters of the character range and convert it
        # into a decimal (from the hex).
        self.start_prefix = int(self.args.start[0:3], 16)
        self.end_prefix = int(self.args.end[0:3], 16)
        self.columns = self.end_prefix - self.start_prefix + 1

        # Start the chart with the boilerplate for XeLaTeX.
        self.log.debug("Writing to " + filename)
        self.open_xelatex(filename)

        # Write out the beginning of the table.
        width = (self.columns + 1)

        self.file.write('\\tabulinesep=1.2mm')
        self.file.write("\\begin{{tabu}} to {0}cm {{X[r]|{1}}}\n"
                        .format(width * 1.2, "X[c,b]|" * width))

        # Write out the first column.
        for column in range(self.start_prefix, self.end_prefix + 1):
            self.file.write("& {0:03x}".format(column))

        self.file.write("\\\\\n")
        self.file.write("\\hline ")

        # We need to figure out which ranges we'll be
        # generating. Start by reporting the full range that we'll be
        # creating.
        self.log.info(
            "Generating file from " + self.args.start +
            " to " + self.args.end)

        # Write out each of the rows in two lines. The first has the glyph
        # and the second has the code.
        for row in range(0, 16):
            # First row has the glyph.
            self.file.write("{0:X} ".format(row))

            for column in range(self.start_prefix, self.end_prefix + 1):
                self.file.write(" &")
                self.file.write("\\vspace{1mm}")
                self.file.write("\\glyphfont{{\\huge{{{0}}}}}".format(
                        self.get_char(column, row)))

            self.file.write("\\\\\n")

            # Second row has the codes.
            self.file.write("".format(row))

            for column in range(self.start_prefix, self.end_prefix + 1):
                self.file.write(" & \\tiny{{{0:03X}{1:X}}}".format(column, row))

            self.file.write("\\\\\n")

            # Finish up with a newline.
            self.file.write("\\hline")
            
            if row != 15:
                self.file.write("\\\n")
            #self.file.write("\\hline \\\\\n")

        # Close the XeLaTeX file.
        self.close_xelatex()

    def get_char(self, column, row):
        if column < 2:
            return ""

        if column == 2 and row == 0:
            return ""

        if column == 7 and row == 15:
            return ""

        code = int("{0:03X}{1:X}".format(column, row), 16)

        if (code == 0x007B or code == 0x007D or code == 0x005F or
            code == 0x0026 or code == 0x0025 or code == 0x0024 or
            code == 0x0023):
            return "\\" + unichr(code)

        if code == 0x007C:
            return "\\textbar";

        if code == 0x005C:
            return "\\textbackslash";

        if code == 0x007E:
            return "\\textasciitilde";

        if code == 0x005E or code == 0x0060:
            return "\\" + unichr(code) + "{}"

        return unichr(code)

    def open_xelatex(self, filename):
        """Opens the XeLaTeX file and generates the opening boilerplate."""

        # Open the file
        self.file = codecs.open(filename, 'w', 'utf-8')

        # Figure out the boilerplate.
        self.file.write("\\documentclass{article}\n")
        self.file.write("\\usepackage{tabu}\n")
        self.file.write("\\usepackage{array}\n")
        self.file.write("\\usepackage{fontspec}\n")
        self.file.write('\usepackage[top=0.5in, bottom=0.5in, left=0.5in, '
                        + "right=0.5in]{geometry}\n")
        self.file.write("\\newfontfamily\\glyphfont[Path={0}/]{{{1}}}\n".format(
                os.path.dirname(self.args.file),
                os.path.basename(self.args.file)))
        self.file.write("\\begin{document}\n")

    def close_xelatex(self):
        # Add in the final XeLaTeX boilerplate.
        self.file.write("\\end{tabu}\n")
        self.file.write("\\end{document}\n")

        # Close the file.
        self.file.close()

    def generate_pdf(self, dirname, chart_filename, pdf_filename):
        """Generates a PDF from the XeLaTeX source."""

        # Generate the source.
        self.log.debug("Generating PDF")
        subprocess.call([
                "xelatex",
                "-output-directory=" + dirname,
                chart_filename,
                pdf_filename])
