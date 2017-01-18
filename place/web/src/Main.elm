import Html exposing (..)
import Html.Attributes exposing (..)
import Html.Events exposing (..)
import WebSocket
import Regex exposing (Regex, regex, contains, escape)

-- import the things from our other Elm file
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
    Changekey newValue ->
      ({ model | key = newValue }, Cmd.none)
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
    SetKey ->
      ({ model | keySet = True }, Cmd.none)
    Scan ->
      ({ model | keySet = False, key = "99999" },
      WebSocket.send "ws://localhost:9130" (makeCmd model))
    Response str ->
      ({ model | response = str }, Cmd.none)



-- SUBSCRIPTIONS
subscriptions : Model -> Sub Msg
subscriptions model =
  WebSocket.keepAlive "ws://localhost:9130"



-- VIEW
view : Model -> Html Msg
view model =
  if model.keySet == False
    then
      askForKey model
    else
      normalPage model

askForKey : Model -> Html Msg
askForKey model =
  div []
    [ h1 [] [ text "PLACE Web Interface" ]
    , h2 [] [ text "Security Key" ]
    , p []
      [ input [ onInput Changekey ] []
      , button [ onClick SetKey ] [ text "Submit Key" ]
      , br [] []
      , keyHelp
      ]
    ]
     
normalPage : Model -> Html Msg
normalPage model =
  div []
    [ h1 [] [ text "PLACE Web Interface" ]
    , p []
      [ text "Command: "
      , code [] [ text (makeCmd model) ]
      ]
    -- SCAN
    , h2 [] [ text "Scan" ]
    , h3 [] [ text "Comments" ]
    , p []
      [ input [ onInput Changecomments ] []
      , br [] []
      , commentsHelp
      ]
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
      ]
    , button [ onClick Scan ] [ text "Scan" ]
    ]

makeCmd : Model -> String
makeCmd model =
  if model.key == "99999"
    then ""
    else model.key ++ " "
      ++ "place_scan"
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

-- helper function
parameterRow : String -> (String -> Msg) -> Html Msg -> Html Msg
parameterRow par func help =
  tr []
    [ td [] [ text ("--"++par) ]
    , td [] [ input [ placeholder ("<"++par++">"), onInput func ] [] ]
    , td [] [ help ]
    ]

