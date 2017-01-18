module PlaceDefaults exposing (..)

import Html exposing (
  Html, div, p, text, em, i, code, strong, sup, ul, li
  )

{-| This is used to initialize the HTML program. -}
placeInit : (Model, Cmd Msg)
placeInit = (placeDefaults, Cmd.none)

{-| The model, or state, of this webapp consists of the values
associated with the command-line arguments for the scan.py script.

*help* and *keySet* are the only boolean value. The rest are consisdered
Strings, although many are actually integer values. However, since
command-line arguments are always passed as strings, this is appropriate
for now. At some point, to assist in data validation, it may be
appropriate to change some of these values to other types.
-}
type alias Model =
  { key     : String
  , keySet  : Bool
  , help    : Bool
  , n       : String
  , n2      : String
  , scan    : String
  , s1      : String
  , s2      : String
  , dm      : String
  , sr      : String
  , tm      : String
  , ch      : String
  , ch2     : String
  , av      : String
  , wt      : String
  , tl      : String
  , tr      : String
  , cr      : String
  , cr2     : String
  , cp      : String
  , cp2     : String
  , ohm     : String
  , ohm2    : String
  , i1      : String
  , d1      : String
  , f1      : String
  , i2      : String
  , d2      : String
  , f2      : String
  , rv      : String
  , rv2     : String
  , dd      : String
  , rg      : String
  , vch     : String
  , sl      : String
  , pp      : String
  , bp      : String
  , so      : String
  , en      : String
  , lm      : String
  , rr      : String
  , pl      : String
  , map     : String
  , comments: String
  , response: String
  }

{-| A Msg is a union type of all the possible functions which change the
PLACE model. -}
type Msg
  = Togglehelp
    | SetKey
    | Changekey      String
    | Changen        String
    | Changen2       String
    | Changescan     String
    | Changes1       String
    | Changes2       String
    | Changedm       String
    | Changesr       String
    | Changetm       String
    | Changech       String
    | Changech2      String
    | Changeav       String
    | Changewt       String
    | Changetl       String
    | Changetr       String
    | Changecr       String
    | Changecr2      String
    | Changecp       String
    | Changecp2      String
    | Changeohm      String
    | Changeohm2     String
    | Changei1       String
    | Changed1       String
    | Changef1       String
    | Changei2       String
    | Changed2       String
    | Changef2       String
    | Changerv       String
    | Changerv2      String
    | Changedd       String
    | Changerg       String
    | Changevch      String
    | Changesl       String
    | Changepp       String
    | Changebp       String
    | Changeso       String
    | Changeen       String
    | Changelm       String
    | Changerr       String
    | Changepl       String
    | Changemap      String
    | Changecomments String
    | Scan
    | Response String

{-| All default values should be placed here to provide one place for
changing them in the future. -}
keyDefault : String
keyDefault = "99999"

keySetDefault : Bool
keySetDefault = False

helpDefault : Bool
helpDefault = False

scanDefault : String
scanDefault = "point"

s1Default : String
s1Default = "long"

s2Default : String
s2Default = "short"

dmDefault : String
dmDefault = "50"

srDefault : String
srDefault = "10M"

{-| The PLACE model is initialized with all the default values. -}
placeDefaults : Model
placeDefaults =
    { key     = keyDefault
    , keySet  = keySetDefault
    , help    = helpDefault
    , n       = ""
    , n2      = ""
    , scan    = scanDefault
    , s1      = s1Default
    , s2      = s2Default
    , dm      = dmDefault
    , sr      = srDefault
    , tm      = ""
    , ch      = ""
    , ch2     = ""
    , av      = ""
    , wt      = ""
    , tl      = ""
    , tr      = ""
    , cr      = ""
    , cr2     = ""
    , cp      = ""
    , cp2     = ""
    , ohm     = ""
    , ohm2    = ""
    , i1      = ""
    , d1      = ""
    , f1      = ""
    , i2      = ""
    , d2      = ""
    , f2      = ""
    , rv      = ""
    , rv2     = ""
    , dd      = ""
    , rg      = ""
    , vch     = ""
    , sl      = ""
    , pp      = ""
    , bp      = ""
    , so      = ""
    , en      = ""
    , lm      = ""
    , rr      = ""
    , pl      = ""
    , map     = ""
    , comments= ""
    , response= ""
    }



-- HELP
tmHelp : Html Msg
tmHelp =
  div []
    [ p [] [ text "Defines time duration for each trace in microseconds." ]
    , p [] [ text "Example: --tm 400 for 400 microsecond traces" ]
    , p [] [ text "Default: 256 microseconds" ]
    , p [] [ em [] [ text "NOTE:" ]
           , text " number of samples will be rounded to next power of two to avoid scrambling data"
           ]
    ]
chHelp : Html Msg
chHelp =
  div []
    [ p [] [ text "Defines oscilloscope card channel to record data." ]
    , p [] [ em [] [ text "NOTE:" ]
           , text " this should be \"Q\" for OSLDV acquisition"
           ]
    , p [] [ text "Example --ch B" ]
    , p [] [ text "Default: A" ]
    ]
ch2Help : Html Msg
ch2Help =
  div []
    [ p [] [ text "Defines oscilloscope card channel to record data." ]
    , p [] [ em [] [ text "NOTE:" ]
           , text " this should be \"I\" for OSLDV acquisition"
           ]
    , p [] [ text "Example --ch2 B" ]
    , p [] [ text "Default: B" ]
    ]
avHelp : Html Msg
avHelp =
  div []
    [ p [] [ text "Define the number of records that shall be averaged." ]
    , p [] [ text "Example: --av 100 to average 100 records" ]
    , p [] [ text "Default: 64 averages" ]
    ]
wtHelp : Html Msg
wtHelp =
  div []
    [ p [] [ text "Time to stall after each stage movement, in seconds. Use to allow residual vibrations to dissipate before recording traces, if necessary." ]
    , p [] [ text "Default: 0" ]
    ]
tlHelp : Html Msg
tlHelp =
  div []
    [ p [] [ text "Trigger level in volts." ]
    , p [] [ text "Default: 1" ]
    ]
trHelp : Html Msg
trHelp =
  div []
    [ p [] [ text "Input range for external trigger in volts." ]
    , p [] [ text "Default: 4" ]
    ]
crHelp : Html Msg
crHelp =
  div []
    [ p [] [ text "Input range of acquisition channel (for --ch and --ch2)." ]
    , p [] [ text "Options ATS660: 200_MV, 400_MV, 800_MV, 2_V, 4_V, 8_V, 16_V" ]
    , p [] [ text "Options ATS9440: 100_MV, 200_MV, 400_MV, 1_V, 2_V, 4_V" ]
    ]
cr2Help : Html Msg
cr2Help = crHelp
cpHelp : Html Msg
cpHelp =
  div []
    [ p [] [ text "Coupling (for --ch and --ch2)." ]
    , p [] [ text "Options: AC, DC" ]
    , p [] [ text "Default: DC coupling" ]
    ]
cp2Help : Html Msg
cp2Help = cpHelp
ohmHelp : Html Msg
ohmHelp =
  div []
    [ p [] [ text "Set impedance of oscilloscope card (for --ch and --ch2)" ]
    , p [] [ text "Options: 50 (50 ohm impedance), 1 (1Mohm impedance)" ]
    , p [] [ text "Default: 50 ohm" ]
    ]
ohm2Help : Html Msg
ohm2Help = ohmHelp
i1Help : Html Msg
i1Help =
  div []
    [ p [] [ text "Define the initial position for dimension 1 stage. Defined in units of corresponding stage: rotation stage (degrees), short and long stage, and picomotors (mm)." ]
    , p [] [ text "Default: 0" ]
    ]
d1Help : Html Msg
d1Help =
  div []
    [ p [] [ text "Define increment for dimension 1 stage. Defined in units of corresponding stage: rotation stage (degrees), short and long stage, and picomotors (mm)." ]
    , p [] [ text "Default: 1" ]
    , p [] [ em [] [ text "NOTE:" ]
           , text " the increment in the header may vary from the value specified for the picomotor results, because the motors will round to the nearest increment number of"
           , i [] [ text " steps" ]
           , text ". The increment in the header is"
           , em [] [ text " correct" ]
           , text "."
           ]
    ]
f1Help : Html Msg
f1Help =
  div []
    [ p []
      [ text "Define the final position for dimension 1 stage. "
      , text "Defined in units of corresponding stage: rotation "
      , text "stage (degrees), short and long stage, and picomotors "
      , text "(mm)."
      ]
    , p [] [ text "Default: 0" ]
    ]
i2Help : Html Msg
i2Help =
  div []
    [ p []
      [ text "Define the initial position for dimension 2 stage. "
      , text "Defined in units of corresponding stage: rotation "
      , text "stage (degrees), short and long stage, and picomotors "
      , text "(mm)."
      ]
    , p [] [ text "Default: 0" ]
    ]
d2Help : Html Msg
d2Help =
  div []
    [ p []
      [ text "Define increment for dimension 2 stage. Defined in "
      , text "units of corresponding stage: rotation stage (degrees), "
      , text "short and long stage, and picomotors (mm)."
      ]
    , p [] [ text "Default: 1" ]
    ]
f2Help : Html Msg
f2Help =
  div []
    [ p []
      [ text "Define the final position for dimension 2 stage. "
      , text "Defined in units of corresponding stage: rotation "
      , text "stage (degrees), short and long stage, and picomotors (mm)"
      ]
    , p []
      [ text "Default: 0" ]
    ]
rvHelp : Html Msg
rvHelp =
  div []
    [ p []
      [ text "Define which receiver to use (for --ch and --ch2)." ]
    , p []
      [ text "Options: polytec, gclad, osldv, none" ]
    , p []
      [ text "Default: none" ]
    ]
rv2Help : Html Msg
rv2Help = rvHelp
ddHelp : Html Msg
ddHelp =
  div []
    [ p []
      [ text "Define decoder for Polytec vibrometer." ]
    , p []
      [ text "Options: VD-08, VD-09, DD-300 (best for ultrasonic "
      , text "applications), and DD-900."
      ]
    , p []
      [ text "Default: DD-300" ]
    ]
rgHelp : Html Msg
rgHelp =
  div []
    [ p []
      [ text "Define range of decoder of Polytec vibrometer. Specify "
      , text "both the value and unit length for the appropriate. See "
      , text "Polytec manual for possible decoders."
      ]
    , p []
      [ text "Example: --rg 5mm specifies a range of 5 mm/s/V." ]
    , p []
      [ text "Default: 5 mm/s/V" ]
    ]
vchHelp : Html Msg
vchHelp =
  div []
    [ p []
      [ text "Define oscilloscope card channel for polytec signal level." ]
    , p []
      [ text "Default: B" ]
    ]
slHelp : Html Msg
slHelp =
  div []
    [ p []
      [ text "Define suitable polytec signal level." ]
    , p []
      [ text "Options: floats range ~0 to 1.1" ]
    , p []
      [ text "Default: 0.90" ]
    ]
ppHelp : Html Msg
ppHelp =
  div []
    [ p []
      [ text "Defines serial port to to communicate with "
      , text "Polytec controller."
      ]
    , p []
      [ text "Default: "
      , code [] [ text "/dev/ttyS0" ]
      ]
    ]
bpHelp : Html Msg
bpHelp =
  div []
    [ p []
      [ text "Defines baudrate for serial communication with "
      , text "Polytec controller."
      ]
    , p []
      [ text "Default: 115200" ]
    ]
soHelp : Html Msg
soHelp =
  div []
    [ p []
      [ text "Defines which source to use." ]
    , p []
      [ text "Options: indi, none" ]
    , p []
      [ text "Default: none" ]
    , p []
      [ strong [] [ text "WARNING" ]
      , text " If "
      , em [] [ text "indi" ]
      , text " is chosen, laser will start automatically!!"
      ]
    ]
enHelp : Html Msg
enHelp =
  div []
    [ p []
      [ text "Specify the energy of the source used (in mJ/cm"
      , sup [] [ text "2" ] -- superscript
      , text ")."
      ]
    , p []
      [ text "Default: 0 mJ/cm"
      , sup [] [ text "2" ] -- superscript
      ]
    , p []
      [ text "If --so is set to "
      , em [] [ text "indi" ]
      , text ":"
      , ul [] -- unordered list
        [ li [] -- list item
          [ text "specify the percentage of maximum percentage of "
          , text "oscillator."
          ]
        ]
      ]
    , p []
      [ text "Default: 0%" ]
    ]
lmHelp : Html Msg
lmHelp =
  div []
    [ p []
      [ text "Specify wavelength of the source used (in nm)." ]
    , p []
      [ text "Default: 1064" ]
    ]
rrHelp : Html Msg
rrHelp =
  div []
    [ p []
      [ text "Specify repetition rate of trigger (in Hz)." ]
    , p []
      [ text "Default: 10" ]
    ]
plHelp : Html Msg
plHelp =
  div []
    [ p []
      [ text "If True will plot traces, if False, plotting is "
      , text "turned off."
      ]
    , p []
      [ text "Default: True" ]
    ]
mapHelp : Html Msg
mapHelp =
  div []
    [ p []
      [ text "Define colormap to use during scan to display image. "
      , text "Choose 'none' if you do not wish to read/plot the "
      , text "2D data."
      ]
    , p []
      [ text "Options: built-in matplotlib colormaps" ]
    , p []
      [ text "Example: --map 'jet' to use jet colormap" ]
    , p []
      [ text "Default: 'gray'" ]
    , p []
      [ em [] [ text "NOTE: " ]
      , text "For large datasets, 'none' is recommended, "
      , text "as it adds significant time to the scan to read and "
      , text "plot the full data set."
      ]
    ]
keyHelp : Html Msg
keyHelp =
  text "For security, please enter the key value displayed on the server console."
commentsHelp : Html Msg
commentsHelp =
  text "Add any extra comments to be added to the trace headers."
