"""Help message, previously in scan_functions.py"""

CLI_HELP = """Command line options:

-h, --help      prints doc string
--n             define the base file name to save data to (data will be
                saved as 'filename.h5' in current directory).

                Default: TestScan
--n2            define the base file name to save second channel data
                to (data will be saved as 'filename.h5' in current
                directory).

                Default: TestScan2
--scan          defines type of scan.

                Options: point, 1D, 2D, dual

                Default: point

                **Note** dual is a two-dimensional scan that moves
                both stages at the same time.
--s1            defines stage for first dimension

                Options: long (1000mm linear stage),
                short (300mm linear stage),
                rot (rotation stage), or
                picox, picoy (picomotor mirrors in x- and y- direction)

                Default: long
--s2            defines stage for second dimension.

                Options: long (1000mm linear stage),
                short (300mm linear stage),
                rot (rotation stage), or
                picox, picoy (picomotor mirrors in x- and y- direction)

                Default: short
--dm            With polytec receiver, defines distance between polytec
                sensor head and scanning mirrors with picomotors (in cm).
                Otherwise, defines distance from picomotors to point of
                interest.  Necessary input for accurate picomotor scanning.

                Default: 50 cm
--sr            defines sample rate. Supply an integer with suffix,
                e.g. 100K for 10e5 samples/second or 1M for 10e6
                samples/second.

                Options ATS9440 and ATS660: 1K, 2K, 5K, 10K, 20K, 50K,
                100K, 200K, 500K, 1M, 2M, 5M, 10M, 20M, 50M, 100M, 125M

                Default: 10M (10 Megasamples/second)
--tm            defines time duration for each trace in microseconds.

                Example: --tm 400 for 400 microsecond traces

                Default: 256 microseconds

                **NOTE** number of samples will be rounded to next power
                of two to avoid scrambling data
--ch            defines oscilloscope card channel to record data.

                **NOTE** this should be "Q" for OSLDV acquisition

                Example --ch B

                Default: A
--ch2           defines oscilloscope card channel to record data.

                **NOTE** this should be "I" for OSLDV acquisition

                Example --ch2 B

                Default: B
--av            define the number of records that shall be averaged.

                Example: --av 100 to average 100 records

                Default: 64 averages
--wt            time to stall after each stage movement, in seconds.
                Use to allow residual vibrations to dissipate before
                recording traces, if necessary.

                Default: 0
--tl            trigger level in volts.

                Default: 1
--tr            input range for external trigger in volts.

                Default: 4
--cr, --cr2     input range of acquisition channel (for --ch and --ch2).

                Options ATS660: 200_MV, 400_MV, 800_MV, 2_V, 4_V, 8_V, 16_V

                Options ATS9440: 100_MV, 200_MV, 400_MV, 1_V, 2_V, 4_V

                Default: +/- 2V
--cp, --cp2     coupling (for --ch and --ch2) .

                Options: AC, DC

                Default: DC coupling.
--ohm, --ohm2   set impedance of oscilloscope card (for --ch and --ch2)

                Options: 50 (50 ohm impedance), 1 (1Mohm impedance)

                Default: 50 ohm
--i1            define the initial position for dimension 1 stage.
                Defined in units of corresponding stage: rotation
                stage (degrees), short and long stage, and picomotors (mm)

                Default: 0
--d1            define increment for dimension 1 stage. Defined in
                units of corresponding stage: rotation stage (degrees),
                short and long stage, and picomotors (mm).

                Default: 1

                **NOTE** the increment in the header may vary from
                the value specified for the picomotor results, because
                the motors will round to the nearest increment number
                of *steps*.  The increment in the header is **correct**.
--f1            define the final position for dimension 1 stage. Defined
                in units of corresponding stage: rotation stage
                (degrees), short and long stage, and picomotors (mm)

                Default: 0
--i2            define the initial position for dimension 2 stage.
                Defined in units of corresponding stage: rotation
                stage (degrees), short and long stage, and picomotors (mm)

                Default: 0
--d2            define increment for dimension 2 stage. Defined in
                units of corresponding stage: rotation stage (degrees),
                short and long stage, and picomotors (mm)

                Default: 1
--f2            define the final position for dimension 2 stage.
                Defined in units of corresponding stage: rotation
                stage (degrees), short and long stage, and picomotors (mm)

                Default: 0
--rv, --rv2     define which receiver to use (for --ch and --ch2).

                Options: polytec, gclad, osldv, none

                Default: none
--dd            define decoder for Polytec vibrometer.

                Options: VD-08, VD-09, DD-300 (best for ultrasonic
                applications), and DD-900

                Default: DD-300
--rg            define range of decoder of Polytec vibrometer. Specify
                both the value and unit length for the appropriate. See
                Polytec manual for possible decoders.

                Example: --rg 5mm specifies a range of 5 mm/s/V.

                Default: 5 mm/s/V
--vch           define oscilloscope card channel for polytec signal level

                Default: B
--sl            define suitable polytec signal level

                Options: floats range ~0 to 1.1

                Default: 0.90
--pp            defines serial port to to communicate with
                Polytec controller.

                Default: '/dev/ttyS0'
--bp            defines baudrate for serial communication with
                Polytec controller.

                Default: 115200
--so            define which source to use.

                Options: indi none

                Default: none

                **WARNING** If 'indi' chosen, laser will start
                automatically!!
--en            specify the energy of the source used (in mJ/cm^2).

                Default: 0 mJ/cm^2

                if --so is set to 'indi:
                    specify the percentage of maximum percentage of
                    oscillator.

                Default: 0 %
--lm            specify wavelength of the source used (in nm)

                Default: 1064
--rr            specify repetition rate of trigger (in Hz)

                Default: 10
--pl            if True will plot traces, if False, plotting is
                turned off.

                Default: True
--map           define colormap to use during scan to display image.
                Choose 'none' if you do not wish to read/plot the
                2D data.

                Options: built-in matplotlib colormaps

                Example: --map 'jet' to use jet colormap

                Default: 'gray'

                **NOTE** for large datasets, 'none' is recommended,
                as it adds significant time to the scan to read and
                plot the full data set.
--comments      add any extra comments to be added to the trace headers

                Example: --comments='Energy at 50.  Phantom with
                no tube.'

                **NOTE** you must have either '  ' or "  " surrounding
                comments
"""
