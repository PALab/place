module PlaceView exposing (..)

{-| This module contains the *View* of the webapp. This means it
contains the bulk of the HTML for drawing what is seen on the screen. It
also has a few helper functions.
-}

import Html exposing (..)
import Html.Events exposing (onClick, onInput)
import Html.Attributes exposing (style, placeholder, defaultValue, value, selected)
import Regex exposing (Regex, regex, contains, escape)
import PlaceDefaults exposing (..)


{-| The main PLACE view.
-}
view : Model -> Html Msg
view model =
    div [ style [ ( "padding", "40px" ) ] ] <|
        placeTitle
            ++ if model.keySet == False then
                preKeyView model
               else
                postKeyView model


{-| This view is always displayed first, and requests the security key
from the user.
-}
preKeyView : Model -> List (Html Msg)
preKeyView model =
    [ p []
        [ b [] [ text "Security Key " ]
        , input [ onInput Changekey ] []
        , button [ onClick SetKey ] [ text "Submit Key" ]
        , br [] []
        , text "For security, please enter the key value displayed on "
        , text "the server console."
        ]
    ]


{-| This view is displayed after the security key is entered. *Note that
the security key is not evaluated until the scan is submitted.*
-}
postKeyView : Model -> List (Html Msg)
postKeyView model =
    [ p []
        [ b [] [ text "Command: " ]
        , code [] [ text (makeCmd model) ]
        , br [] []
        , button [ onClick Scan ] [ text "Scan" ]
        ]
    ]
        ++ [ p []
                [ b [] [ text "Comments " ]
                , input [ onInput Changecomments ] []
                , br [] []
                , text "Add any extra comments to be added to the trace headers."
                ]
           ]
        ++ scanView model
        ++ osciView model
        ++ [ h2 [] [ text "Other options (in development)" ]
           , h3 [] [ text "dm" ]
           , p []
                [ input [ defaultValue placeDefaults.dm, onInput Changedm ] []
                , text (" Default: " ++ placeDefaults.dm)
                , br [] []
                , text "With polytech receiver, defines distance between polytec "
                , text "sensor head and scanning mirrors with picomotors (in "
                , text "cm). Otherwise, defines distance from picomotors to "
                , text "point of interest.  Necessary input for accurate "
                , text "picomotor scanning."
                ]
           , table []
                [ parameterRow "rv" Changerv rvHelp
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
                ]
           ]


placeTitle : List (Html Msg)
placeTitle =
    [ h1 [] [ text "PLACE Web Interface" ] ]


scanView : Model -> List (Html Msg)
scanView model =
    [ h2 [] [ text "Scan" ]
    , select [ onInput Changescan ]
        [ option [ value "point", selected (model.scan == "point") ] [ text "Point" ]
        , option [ value "1D", selected (model.scan == "1D") ] [ text "1D" ]
        , option [ value "2D", selected (model.scan == "2D") ] [ text "2D" ]
        , option [ value "dual", selected (model.scan == "dual") ] [ text "Dual" ]
        ]
    ]
        ++ (if model.scan == "dual" then
                [ br [] []
                , em [] [ text " NOTE: Dual" ]
                , text " is a two-dimensional scan that moves both stages at"
                , text " the same time."
                ]
            else
                []
           )
        ++ (if model.scan == "1D" || model.scan == "2D" || model.scan == "dual" then
                [ stage1View model ]
            else
                []
           )
        ++ (if model.scan == "2D" || model.scan == "dual" then
                [ stage2View model ]
            else
                []
           )
        ++ (if model.scan == "1D" || model.scan == "2D" || model.scan == "dual" then
                [ b [] [ text "Stage wait time " ]
                , input [ defaultValue placeDefaults.wt, onInput Changewt ] []
                , br [] []
                , text "Time to stall after each stage movement, in seconds. "
                , text "Use to allow residual vibrations to dissipate before "
                , text "recording traces, if necessary."
                ]
            else
                []
           )
        ++ [ p []
                [ b [] [ text "Sample rate " ]
                , selectSampleRate
                , br [] []
                , text "Defines sample rate. Supply an integer with suffix, e.g. "
                , text "100K for 10e5 samples/second or 1M for 10e6 samples/"
                , text "second."
                ]
           ]
        ++ [ p []
                [ text "Data will be saved to this filename. "
                , input [ onInput Changen ] []
                , text ".h5"
                ]
           , p []
                [ text "Second channel data will be saved to this filename. "
                , input [ onInput Changen2 ] []
                , text ".h5"
                ]
           ]


osciView : Model -> List (Html Msg)
osciView model =
    [ h2 [] [ text "Oscilloscope" ] ]
        ++ if model.osci == "none" then
            [ selectOscilloscope model ]
           else
            [ selectOscilloscope model
            , p []
                [ b [] [ text "Duration " ]
                , input [ defaultValue placeDefaults.tm, onInput Changetm ] []
                , br [] []
                , text "Defines time duration for each trace in microseconds."
                , br [] []
                , em [] [ text "Note:" ]
                , text " number of samples will be rounded to next power of two"
                , text " to avoid scrambling data."
                ]
            , p []
                [ b [] [ text "Channel 1 " ]
                , selectChannel1 model.osci
                , br [] []
                , text "Defines oscilloscope card channel to record data."
                , br [] []
                , em [] [ text "Note:" ]
                , text " this should be \"Q\" for OSLDV acquisition."
                , br [] []
                , b [] [ text "Range " ]
                , selectRange Changecr model.osci
                , br [] []
                , text "Input range of acquisition channel."
                , br [] []
                , b [] [ text "Coupling " ]
                , selectCoupling Changecp
                , br [] []
                , b [] [ text "Impedance " ]
                , selectImpedance Changeohm
                ]
            , p []
                [ b [] [ text "Channel 2 " ]
                , selectChannel2 model
                , br [] []
                , text "Defines oscilloscope card channel to record data."
                , br [] []
                , em [] [ text "Note:" ]
                , text " this should be \"I\" for OSLDV acquisition."
                , br [] []
                , b [] [ text "Range " ]
                , selectRange Changecr2 model.osci
                , br [] []
                , text "Input range of acquisition channel."
                , br [] []
                , b [] [ text "Coupling " ]
                , selectCoupling Changecp2
                , br [] []
                , b [] [ text "Impedance " ]
                , selectImpedance Changeohm2
                ]
            , p []
                [ b [] [ text "Averages " ]
                , input [ defaultValue placeDefaults.av, onInput Changeav ] []
                , br [] []
                , text "Define the number of records that shall be averaged."
                ]
            , p []
                [ b [] [ text "Trigger" ]
                , br [] []
                , text "Level: "
                , input [ defaultValue placeDefaults.tl, onInput Changetl ] []
                , text " volts"
                , br [] []
                , text "Input range for external trigger: "
                , input [ defaultValue placeDefaults.tr, onInput Changetr ] []
                , text " volts"
                ]
            ]


{-| A subview displaying the options for the first stage.
-}
stage1View : Model -> Html Msg
stage1View model =
    p []
        [ b [] [ text "Stage for first dimension " ]
        , select [ onInput Changes1 ]
            [ option [ value "short" ] [ text "300mm linear stage" ]
            , option [ value placeDefaults.s1, selected True ] [ text "1000mm linear stage" ]
            , option [ value "rot" ] [ text "rotation stage" ]
            , option [ value "picox" ] [ text "picomotor mirrors (x-direction)" ]
            , option [ value "picoy" ] [ text "picomotor mirrors (y-direction)" ]
            ]
        , br [] []
        , (if model.s1 == "rot" then
            text "Stage rotation (degrees): "
           else
            text "Stage movement (mm): "
          )
        , ul []
            [ li []
                [ text "Start position: "
                , input [ defaultValue placeDefaults.i1, onInput Changei1 ] []
                ]
            , li []
                [ text "Position increment: "
                , input [ defaultValue placeDefaults.d1, onInput Changed1 ] []
                ]
            , li []
                [ text "Finish position: "
                , input [ defaultValue placeDefaults.f1, onInput Changef1 ] []
                ]
            ]
        ]


{-| A subview displaying the options for the second stage.
-}
stage2View : Model -> Html Msg
stage2View model =
    p []
        [ b [] [ text "Stage for second dimension " ]
        , select [ onInput Changes2 ]
            [ option [ value placeDefaults.s2, selected True ] [ text "300mm linear stage" ]
            , option [ value "long" ] [ text "1000mm linear stage" ]
            , option [ value "rot" ] [ text "rotation stage" ]
            , option [ value "picox" ] [ text "picomotor mirrors (x-direction)" ]
            , option [ value "picoy" ] [ text "picomotor mirrors (y-direction)" ]
            ]
        , br [] []
        , (if model.s2 == "rot" then
            text "Stage rotation (degrees): "
           else
            text "Stage movement (mm): "
          )
        , ul []
            [ li []
                [ text "Start position: "
                , input [ defaultValue placeDefaults.i2, onInput Changei2 ] []
                ]
            , li []
                [ text "Position increment: "
                , input [ defaultValue placeDefaults.d2, onInput Changed2 ] []
                ]
            , li []
                [ text "Finish position: "
                , input [ defaultValue placeDefaults.f2, onInput Changef2 ] []
                ]
            ]
        ]


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
showArgOmitBlank : String -> String -> String
showArgOmitBlank opt value =
    case value of
        "" ->
            ""

        otherwise ->
            showArg opt value


showArg : String -> String -> String
showArg opt value =
    if contains disallowed value then
        " --" ++ opt ++ " \"(invalid characters)\""
    else
        " --" ++ opt ++ " \"" ++ value ++ "\""


makeCmd : Model -> String
makeCmd model =
    "place_scan"
        ++ (showArgOmitBlank "n" model.n)
        ++ (showArgOmitBlank "n2" model.n2)
        ++ (showArgOmitBlank "scan" model.scan)
        ++ (if model.scan == "1D" || model.scan == "2D" || model.scan == "dual" then
                (showArg "s1" model.s1)
                    ++ (showArg "i1" model.i1)
                    ++ (showArg "d1" model.d1)
                    ++ (showArg "f1" model.f1)
            else
                ""
           )
        ++ (if model.scan == "2D" || model.scan == "dual" then
                (showArg "s2" model.s2)
                    ++ (showArg "i2" model.i2)
                    ++ (showArg "d2" model.d2)
                    ++ (showArg "f2" model.f2)
            else
                ""
           )
        ++ (if model.scan == "1D" || model.scan == "2D" || model.scan == "dual" then
                (showArg "wt" model.wt)
            else
                ""
           )
        ++ (showArgOmitBlank "dm" model.dm)
        ++ (showArgOmitBlank "sr" model.sr)
        ++ (if model.osci /= "none" then
                (showArgOmitBlank "tm" model.tm)
                    ++ (showArgOmitBlank "av" model.av)
                    ++ (showArgOmitBlank "tl" model.tl)
                    ++ (showArgOmitBlank "tr" model.tr)
                    ++ (showArgOmitBlank "ch" model.ch)
                    ++ (showArgOmitBlank "cr" model.cr)
                    ++ (showArgOmitBlank "cp" model.cp)
                    ++ (showArgOmitBlank "ohm" model.ohm)
                    ++ (showArgOmitBlank "ch2" model.ch2)
                    ++ (showArgOmitBlank "cr2" model.cr2)
                    ++ (showArgOmitBlank "cp2" model.cp2)
                    ++ (showArgOmitBlank "ohm2" model.ohm2)
            else
                ""
           )
        ++ (showArgOmitBlank "rv" model.rv)
        ++ (showArgOmitBlank "rv2" model.rv2)
        ++ (showArgOmitBlank "dd" model.dd)
        ++ (showArgOmitBlank "rg" model.rg)
        ++ (showArgOmitBlank "vch" model.vch)
        ++ (showArgOmitBlank "sl" model.sl)
        ++ (showArgOmitBlank "pp" model.pp)
        ++ (showArgOmitBlank "bp" model.bp)
        ++ (showArgOmitBlank "so" model.so)
        ++ (showArgOmitBlank "en" model.en)
        ++ (showArgOmitBlank "lm" model.lm)
        ++ (showArgOmitBlank "rr" model.rr)
        ++ (showArgOmitBlank "pl" model.pl)
        ++ (showArgOmitBlank "map" model.map)
        ++ (showArgOmitBlank "comments" model.comments)


parameterRow : String -> (String -> Msg) -> Html Msg -> Html Msg
parameterRow par func help =
    tr []
        [ td [] [ text ("--" ++ par) ]
        , td [] [ input [ placeholder ("<" ++ par ++ ">"), onInput func ] [] ]
        , td [] [ help ]
        ]


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
    String.fromList [ '"', '$', '`', '\\', '!' ]
        |> escape
        |> \x ->
            "["
                ++ x
                ++ "]"
                |> regex


{-| Html selector for sample rates.
-}
selectSampleRate : Html Msg
selectSampleRate =
    select [ onInput Changesr ]
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
        , option [ value placeDefaults.sr, selected True ] [ text "10M" ]
        , option [ value "20M" ] [ text "20M" ]
        , option [ value "50M" ] [ text "50M" ]
        , option [ value "100M" ] [ text "100M" ]
        , option [ value "125M" ] [ text "125M" ]
        ]


selectOscilloscope : Model -> Html Msg
selectOscilloscope model =
    select [ onInput Changeosci ]
        [ option [ value "none", selected (model.osci == "none") ] [ text "none" ]
        , option [ value "ATS660", selected (model.osci == "ATS660") ] [ text "ATS660" ]
        , option [ value "ATS9440", selected (model.osci == "ATS9440") ] [ text "ATS9440" ]
        , option [ value "other", selected (model.osci == "other") ] [ text "other" ]
        ]


selectRange : (String -> Msg) -> String -> Html Msg
selectRange change osci =
    case osci of
        "ATS660" ->
            select [ onInput change ]
                [ option [ value "200_MV", selected True ] [ text "200mV" ]
                , option [ value "400_MV" ] [ text "400mV" ]
                , option [ value "800_MV" ] [ text "800mV" ]
                , option [ value "2_V" ] [ text "2V" ]
                , option [ value "4_V" ] [ text "4V" ]
                , option [ value "8_V" ] [ text "8V" ]
                , option [ value "16_V" ] [ text "16V" ]
                ]

        "ATS9440" ->
            select [ onInput change ]
                [ option [ value "100_MV" ] [ text "100mV" ]
                , option [ value "200_MV", selected True ] [ text "200mV" ]
                , option [ value "400_MV" ] [ text "400mV" ]
                , option [ value "1_V" ] [ text "1V" ]
                , option [ value "2_V" ] [ text "2V" ]
                , option [ value "4_V" ] [ text "4V" ]
                ]

        otherwise ->
            input [ onInput change ] []


selectChannel1 : String -> Html Msg
selectChannel1 osci =
    case osci of
        "ATS660" ->
            select [ onInput Changech ]
                [ option [ value "A", selected True ] [ text "A" ]
                , option [ value "B" ] [ text "B" ]
                ]

        "ATS9440" ->
            select [ onInput Changech ]
                [ option [ value "A", selected True ] [ text "A" ]
                , option [ value "B" ] [ text "B" ]
                , option [ value "C" ] [ text "C" ]
                , option [ value "D" ] [ text "D" ]
                ]

        otherwise ->
            input [ onInput Changech ] []


selectChannel2 : Model -> Html Msg
selectChannel2 model =
    case model.osci of
        "ATS660" ->
            select [ onInput Changech2 ]
                [ option [ value "A", selected (model.ch2 == "A") ] [ text "A" ]
                , option [ value "B", selected (model.ch2 == "B") ] [ text "B" ]
                ]

        "ATS9440" ->
            select [ onInput Changech2 ]
                [ option [ value "A", selected (model.ch2 == "A") ] [ text "A" ]
                , option [ value "B", selected (model.ch2 == "B") ] [ text "B" ]
                , option [ value "C", selected (model.ch2 == "C") ] [ text "C" ]
                , option [ value "D", selected (model.ch2 == "D") ] [ text "D" ]
                ]

        otherwise ->
            input [ onInput Changech2 ] []


selectCoupling : (String -> Msg) -> Html Msg
selectCoupling change =
    select [ onInput change ]
        [ option [ value "AC" ] [ text "AC" ]
        , option [ value "DC", selected True ] [ text "DC" ]
        ]


selectImpedance : (String -> Msg) -> Html Msg
selectImpedance change =
    select [ onInput change ]
        [ option [ value "50", selected True ] [ text "50 ohm" ]
        , option [ value "1" ] [ text "1 Mohm" ]
        ]
