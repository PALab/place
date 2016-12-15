import Html exposing (..)
import Html.Attributes exposing (..)
import Html.Events exposing (..)
import WebSocket
import Regex exposing (Regex, regex, contains, escape)

import PlaceDefaults exposing (..)


{-| A webapp for interfacing with the included scan.py script. It is
still very much in development.
-}
main : Program Never Model Msg
main =
  Html.program
    { init = PlaceDefaults.placeInit
    , view = view
    , update = update
    , subscriptions = subscriptions
    }


update : Msg -> Model -> (Model, Cmd Msg)
update msg model =
  case msg of
    Togglehelp ->
      ({ model | help = not model.help }, Cmd.none)
    Changen newValue ->
      ({ model | n = newValue }, Cmd.none)
    Changen2 newValue ->
      ({ model | n2 = newValue }, Cmd.none)
    Changescan newValue ->
      ({ model | scan = newValue }, Cmd.none)
    Changes1 newValue ->
      ({ model | s1 = newValue }, Cmd.none)
    Changes2 newValue ->
      ({ model | s2 = newValue }, Cmd.none)
    Changedm newValue ->
      ({ model | dm = newValue }, Cmd.none)
    Changesr newValue ->
      ({ model | sr = newValue }, Cmd.none)
    Changetm newValue ->
      ({ model | tm = newValue }, Cmd.none)
    Changech newValue ->
      ({ model | ch = newValue }, Cmd.none)
    Changech2 newValue ->
      ({ model | ch2 = newValue }, Cmd.none)
    Changeav newValue ->
      ({ model | av = newValue }, Cmd.none)
    Changewt newValue ->
      ({ model | wt = newValue }, Cmd.none)
    Changetl newValue ->
      ({ model | tl = newValue }, Cmd.none)
    Changetr newValue ->
      ({ model | tr = newValue }, Cmd.none)
    Changecr newValue ->
      ({ model | cr = newValue }, Cmd.none)
    Changecr2 newValue ->
      ({ model | cr2 = newValue }, Cmd.none)
    Changecp newValue ->
      ({ model | cp = newValue }, Cmd.none)
    Changecp2 newValue ->
      ({ model | cp2 = newValue }, Cmd.none)
    Changeohm newValue ->
      ({ model | ohm = newValue }, Cmd.none)
    Changeohm2 newValue ->
      ({ model | ohm2 = newValue }, Cmd.none)
    Changei1 newValue ->
      ({ model | i1 = newValue }, Cmd.none)
    Changed1 newValue ->
      ({ model | d1 = newValue }, Cmd.none)
    Changef1 newValue ->
      ({ model | f1 = newValue }, Cmd.none)
    Changei2 newValue ->
      ({ model | i2 = newValue }, Cmd.none)
    Changed2 newValue ->
      ({ model | d2 = newValue }, Cmd.none)
    Changef2 newValue ->
      ({ model | f2 = newValue }, Cmd.none)
    Changerv newValue ->
      ({ model | rv = newValue }, Cmd.none)
    Changerv2 newValue ->
      ({ model | rv2 = newValue }, Cmd.none)
    Changedd newValue ->
      ({ model | dd = newValue }, Cmd.none)
    Changerg newValue ->
      ({ model | rg = newValue }, Cmd.none)
    Changevch newValue ->
      ({ model | vch = newValue }, Cmd.none)
    Changesl newValue ->
      ({ model | sl = newValue }, Cmd.none)
    Changepp newValue ->
      ({ model | pp = newValue }, Cmd.none)
    Changebp newValue ->
      ({ model | bp = newValue }, Cmd.none)
    Changeso newValue ->
      ({ model | so = newValue }, Cmd.none)
    Changeen newValue ->
      ({ model | en = newValue }, Cmd.none)
    Changelm newValue ->
      ({ model | lm = newValue }, Cmd.none)
    Changerr newValue ->
      ({ model | rr = newValue }, Cmd.none)
    Changepl newValue ->
      ({ model | pl = newValue }, Cmd.none)
    Changemap newValue ->
      ({ model | map = newValue }, Cmd.none)
    Changecomments newValue ->
      ({ model | comments = newValue }, Cmd.none)
    Scan ->
      (model, WebSocket.send "ws://localhost:9130" (makeCmd model))
    Response str ->
      ({ model | response = str }, Cmd.none)



-- SUBSCRIPTIONS


subscriptions : Model -> Sub Msg
subscriptions model =
  WebSocket.listen "ws://localhost:9130" Response



-- VIEW


parameterRow : String -> (String -> Msg) -> Html Msg -> Html Msg
parameterRow par func help =
  tr []
    [ td [] [ text ("--"++par) ]
    , td [] [ input [ placeholder ("<"++par++">"), onInput func ] [] ]
    , td [] [ help ]
    ]

view : Model -> Html Msg
view model =
  Html.form []
    [ h1 [] [ text "PLACE Web Interface" ]
    , p [] [ code [] [ text (makeCmd model) ] ]
    -- SCAN
    , h2 [] [ text "Scan" ]
    , h3 [] [ text "Type of scan" ]
    , p []
      [ select [ onInput Changescan ]
        [ option [ value scanDefault, selected True ] [ text "Point" ]
        , option [ value "1D" ] [ text "1D" ]
        , option [ value "2D" ] [ text "2D" ]
        , option [ value "dual" ] [ text "Dual" ]
        ]
      , text " Default: Point"
      , br [] []
      , em [] [ text "NOTE: Dual" ]
      , text " is a two-dimensional scan that moves both stages at"
      , text " the same time."
      ]
    , h3 [] [ text "Sample rate" ]
    , p []
      [ select [ onInput Changesr ]
        [ option [ value "1K" ] [ text "1K" ]
        , option [ value "2K" ] [ text "2K" ]
        , option [ value "5K" ] [ text "5K" ]
        , option [ value "10K" ] [ text "10K" ]
        , option [ value "20K" ] [ text "20K" ]
        , option [ value "50K" ] [ text "50K" ]
        , option [ value "100K" ] [ text "100K" ]
        , option [ value "200K" ] [ text "200K" ]
        , option [ value "500K" ] [ text "500K" ]
        , option [ value "1M" ] [ text "1M" ]
        , option [ value "2M" ] [ text "2M" ]
        , option [ value "5M" ] [ text "5M" ]
        , option [ value srDefault, selected True ] [ text "10M" ]
        , option [ value "20M" ] [ text "20M" ]
        , option [ value "50M" ] [ text "50M" ]
        , option [ value "100M" ] [ text "100M" ]
        , option [ value "125M" ] [ text "125M" ]
        ]
      , text (" Default: " ++ srDefault)
      , br [] []
      , text "Defines sample rate. Supply an integer with suffix, e.g. "
      , text "100K for 10e5 samples/second or 1M for 10e6 samples/"
      , text "second."
      ]
    , h3 [] [ text "Stage for first dimension" ]
    , p []
      [ select [ onInput Changes1 ]
        [ option [ value "short" ] [ text "300mm linear stage" ]
        , option [ value s1Default, selected True ] [ text "1000mm linear stage" ]
        , option [ value "rot" ] [ text "rotation stage" ]
        , option [ value "picox" ] [ text "picomotor mirrors (x-direction)" ]
        , option [ value "picoy" ] [ text "picomotor mirrors (y-direction)" ]
        ]
      ]
    , h3 [] [ text "Stage for second dimension" ]
    , p []
      [ select [ onInput Changes2 ]
        [ option [ value s2Default, selected True ] [ text "300mm linear stage" ]
        , option [ value "long" ] [ text "1000mm linear stage" ]
        , option [ value "rot" ] [ text "rotation stage" ]
        , option [ value "picox" ] [ text "picomotor mirrors (x-direction)" ]
        , option [ value "picoy" ] [ text "picomotor mirrors (y-direction)" ]
        ]
      ]
    -- FILES
    , h2 [] [ text "Files" ]
    , p []
      [ input [ onInput Changen ] []
      , text ".h5"
      , br [] []
      , text "Data will be saved to this filename."
      ]
    , p []
      [ input [ onInput Changen2 ] []
      , text ".h5"
      , br [] []
      , text "Second channel data will be saved to this filename."
      ]
    -- OTHER OPTIONS
    , h2 [] [ text "Other options" ]
    , h3 [] [ text "dm" ]
    , p []
      [ input [ defaultValue dmDefault, onInput Changedm ] []
      , text (" Default: " ++ dmDefault)
      , br [] []
      , text "With polytech receiver, defines distance between polytec "
      , text "sensor head and scanning mirrors with picomotors (in "
      , text "cm). Otherwise, defines distance from picomotors to "
      , text "point of interest.  Necessary input for accurate "
      , text "picomotor scanning."
      ]
    , table []
      [ parameterRow "tm" Changetm tmHelp
      , parameterRow "ch" Changech chHelp
      , parameterRow "ch2" Changech2 ch2Help
      , parameterRow "av" Changeav avHelp
      , parameterRow "wt" Changewt wtHelp
      , parameterRow "tl" Changetl tlHelp
      , parameterRow "tr" Changetr trHelp
      , parameterRow "cr" Changecr crHelp
      , parameterRow "cr2" Changecr2 cr2Help
      , parameterRow "cp" Changecp cpHelp
      , parameterRow "cp2" Changecp2 cp2Help
      , parameterRow "ohm" Changeohm ohmHelp
      , parameterRow "ohm2" Changeohm2 ohm2Help
      , parameterRow "i1" Changei1 i1Help
      , parameterRow "d1" Changed1 d1Help
      , parameterRow "f1" Changef1 f1Help
      , parameterRow "i2" Changei2 i2Help
      , parameterRow "d2" Changed2 d2Help
      , parameterRow "f2" Changef2 f2Help
      , parameterRow "rv" Changerv rvHelp
      , parameterRow "rv2" Changerv2 rv2Help
      , parameterRow "dd" Changedd ddHelp
      , parameterRow "rg" Changerg rgHelp
      , parameterRow "vch" Changevch vchHelp
      , parameterRow "sl" Changesl slHelp
      , parameterRow "pp" Changepp ppHelp
      , parameterRow "bp" Changebp bpHelp
      , parameterRow "so" Changeso soHelp
      , parameterRow "en" Changeen enHelp
      , parameterRow "lm" Changelm lmHelp
      , parameterRow "rr" Changerr rrHelp
      , parameterRow "pl" Changepl plHelp
      , parameterRow "map" Changemap mapHelp
      , parameterRow "comments" Changecomments commentsHelp
      ]
    , button [ onClick Scan ] [ text "Scan" ]
    , div [] [ text model.response ]
    ]

makeCmd : Model -> String
makeCmd model =
  if model.help
     then "python3 scan.py --help"
     else "python3 scan.py"
      ++ (checkOption "n"     model.n   )
      ++ (checkOption "n2"    model.n2  )
      ++ (checkOption "scan"  model.scan)
      ++ (checkOption "s1"    model.s1  )
      ++ (checkOption "s2"    model.s2  )
      ++ (checkOption "dm"    model.dm  )
      ++ (checkOption "sr"    model.sr  )
      ++ (checkOption "tm"    model.tm  )
      ++ (checkOption "ch"    model.ch  )
      ++ (checkOption "ch2"   model.ch2 )
      ++ (checkOption "av"    model.av  )
      ++ (checkOption "wt"    model.wt  )
      ++ (checkOption "tl"    model.tl  )
      ++ (checkOption "tr"    model.tr  )
      ++ (checkOption "cr"    model.cr  )
      ++ (checkOption "cr2"   model.cr2 )
      ++ (checkOption "cp"    model.cp  )
      ++ (checkOption "cp2"   model.cp2 )
      ++ (checkOption "ohm"   model.ohm )
      ++ (checkOption "ohm2"  model.ohm2)
      ++ (checkOption "i1"    model.i1  )
      ++ (checkOption "d1"    model.d1  )
      ++ (checkOption "f1"    model.f1  )
      ++ (checkOption "i2"    model.i2  )
      ++ (checkOption "d2"    model.d2  )
      ++ (checkOption "f2"    model.f2  )
      ++ (checkOption "rv"    model.rv  )
      ++ (checkOption "rv2"   model.rv2 )
      ++ (checkOption "dd"    model.dd  )
      ++ (checkOption "rg"    model.rg  )
      ++ (checkOption "vch"   model.vch )
      ++ (checkOption "sl"    model.sl  )
      ++ (checkOption "pp"    model.pp  )
      ++ (checkOption "bp"    model.bp  )
      ++ (checkOption "so"    model.so  )
      ++ (checkOption "en"    model.en  )
      ++ (checkOption "lm"    model.lm  )
      ++ (checkOption "rr"    model.rr  )
      ++ (checkOption "pl"    model.pl  )
      ++ (checkOption "map"   model.map )
      ++ (checkOption "comments" model.comments)

{-| Construct strings of parameters and values. The values for each
parameter are stored in the model. If the value is the empty string,
then we can return the empty string. Otherwise, we return the option
with the value prepended.

Also, note that values which include spaces must be quoted, so this test
is performed as well.

TODO: Validation needs to be performed to increase security. For
example, comments should only be allowed alphanumeric data and spaces to
prevent the webapp from being able to send programmatic data into the
receiving application.
-}
checkOption : String -> String -> String
checkOption opt value =
  case value of
    "" -> ""
    otherwise ->
      if contains disallowed value
         then " --" ++ opt ++ " \"(invalid characters)\""
         else " --" ++ opt ++ " \"" ++ value ++ "\""

{-| It is important that data sent from this webapp is not able to
execute malicious code on the server. Therefore, the user input values
for command line parameters are quoted and may not contain special
characters which have special meaning within the quoted environment.

At the present time, this includes the following characters: " $ ` \ !

These characters were taken from the follow webpage:
https://www.gnu.org/software/bash/manual/html_node/Double-Quotes.html

This function generates a regex string to test for these special
characters. It uses the built-in Regex library to ensure that the
resulting regular expression is correct.

**Note:** It should technically be the responsibility of scan.py to
validate the data received from this webapp. From a security standpoint,
checking for the following characters should be unnecessary. At some
future point, if this webapp is running slow and validation on the other
end is guaranteed to be secure, then this could be removed.
-}
disallowed : Regex
disallowed =
  String.fromList ['"','$','`','\\','!']
  |> escape
  |> \x -> "[" ++ x ++ "]"
  |> regex

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
commentsHelp : Html Msg
commentsHelp =
  div []
    [ p []
      [ text "Add any extra comments to be added to the"
      , text " trace headers."
      ]
    ]
