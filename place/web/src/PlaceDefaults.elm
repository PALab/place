module PlaceDefaults exposing (..)

import Html exposing (..)


{-| The model, or state, of this webapp consists of the values
associated with the command-line arguments for the scan.py script.

*help* and *keySet* are the only boolean value. The rest are consisdered
Strings, although many are actually integer values. However, since
command-line arguments are always passed as strings, this is appropriate
for now. At some point, to assist in data validation, it may be
appropriate to change some of these values to other types.
-}
type alias Model =
    { key : String
    , keySet : Bool
    , help : Bool
    , n : String
    , n2 : String
    , scan : String
    , s1 : String
    , s2 : String
    , dm : String
    , sr : String
    , tm : String
    , ch : String
    , ch2 : String
    , av : String
    , wt : String
    , tl : String
    , tr : String
    , cr : String
    , cr2 : String
    , cp : String
    , cp2 : String
    , ohm : String
    , ohm2 : String
    , i1 : String
    , d1 : String
    , f1 : String
    , i2 : String
    , d2 : String
    , f2 : String
    , rv : String
    , rv2 : String
    , dd : String
    , rg : String
    , vch : String
    , sl : String
    , pp : String
    , bp : String
    , so : String
    , en : String
    , lm : String
    , rr : String
    , pl : String
    , map : String
    , comments : String
    , response : String
    , osci : String
    }


{-| The PLACE model is initialized with all the default values.
-}
placeDefaults : Model
placeDefaults =
    { key = "99999"
    , keySet = False
    , help = False
    , n = ""
    , n2 = ""
    , scan = "point"
    , s1 = "long"
    , s2 = "short"
    , dm = "50"
    , sr = "10M"
    , tm = "256"
    , ch = "A"
    , ch2 = "B"
    , av = "64"
    , wt = "0"
    , tl = "1"
    , tr = "4"
    , cr = "200_MV"
    , cr2 = "200_MV"
    , cp = "DC"
    , cp2 = "DC"
    , ohm = "50"
    , ohm2 = "50"
    , i1 = "0"
    , d1 = "1"
    , f1 = "0"
    , i2 = "0"
    , d2 = "1"
    , f2 = "0"
    , rv = ""
    , rv2 = ""
    , dd = ""
    , rg = ""
    , vch = ""
    , sl = ""
    , pp = ""
    , bp = ""
    , so = ""
    , en = ""
    , lm = ""
    , rr = ""
    , pl = ""
    , map = ""
    , comments = ""
    , response = ""
    , osci = "none"
    }


{-| A Msg is a union type of all the possible functions which change the
PLACE model.
-}
type Msg
    = Togglehelp
    | SetKey
    | Changekey String
    | Changen String
    | Changen2 String
    | Changescan String
    | Changes1 String
    | Changes2 String
    | Changedm String
    | Changesr String
    | Changetm String
    | Changech String
    | Changech2 String
    | Changeav String
    | Changewt String
    | Changetl String
    | Changetr String
    | Changecr String
    | Changecr2 String
    | Changecp String
    | Changecp2 String
    | Changeohm String
    | Changeohm2 String
    | Changei1 String
    | Changed1 String
    | Changef1 String
    | Changei2 String
    | Changed2 String
    | Changef2 String
    | Changerv String
    | Changerv2 String
    | Changedd String
    | Changerg String
    | Changevch String
    | Changesl String
    | Changepp String
    | Changebp String
    | Changeso String
    | Changeen String
    | Changelm String
    | Changerr String
    | Changepl String
    | Changemap String
    | Changecomments String
    | Scan
    | Response String
    | Changeosci String



-- HELP


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
rv2Help =
    rvHelp


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
            , sup [] [ text "2" ]
              -- superscript
            , text ")."
            ]
        , p []
            [ text "Default: 0 mJ/cm"
            , sup [] [ text "2" ]
              -- superscript
            ]
        , p []
            [ text "If --so is set to "
            , em [] [ text "indi" ]
            , text ":"
            , ul []
                -- unordered list
                [ li []
                    -- list item
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
