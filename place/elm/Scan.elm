port module Scan exposing (Scan, requestJson, jsonData)

{-| This module handles the web interface for a PLACE scan.

# Definition
@docs Scan

# Ports
@docs requestJson, jsonData
-}

import Html exposing (Html, div, h1, text, br, pre, button, option, select)
import Html.Events exposing (onClick, onInput)
import Html.Attributes exposing (id, selected, value)
import Json.Encode exposing (encode, object)
import List exposing (head, filter)
import Instrument exposing (Instrument)


-----------------------
-- EXPOSED INTERFACE --
-----------------------


{-| A scan is currently just a type and a list of instruments. Instruments are
responsible for their own configuration.
-}
type alias Scan =
    { scan_type : String
    , instruments : List Instrument
    }


{-| When this command is sent to a plugin, the plugin should reply with its
JSON data.
-}
port requestJson : String -> Cmd msg


{-| The module will listen on this port for JSON data from plugins.
-}
port jsonData : (Json.Encode.Value -> msg) -> Sub msg



----------
-- VIEW --
----------


view : Scan -> Html Msg
view scan =
    div []
        [ h1 [] [ text "PLACE interface" ]
        , text "Scan type: "
        , select [ onInput ChangeScanType ]
            [ option
                [ value "None", selected (scan.scan_type == "None") ]
                [ text "None" ]
            , option
                [ value "scan_point_test", selected (scan.scan_type == "scan_point_test") ]
                [ text "Point scan (test)" ]
            ]
        , br [] []
        , button [ onClick RequestJson ] [ text "Scan" ] {- debug code -}
        , br [] []
        , pre []
            [ text <|
                encode 4 <|
                    object
                        [ ( "scan_type", Json.Encode.string scan.scan_type )
                        , ( "instruments", Instrument.encoder scan.instruments )
                        ]
            ]
          {- end debug code -}
        ]



------------
-- UPDATE --
------------


type Msg
    = ChangeScanType String
    | UpdateInstruments Json.Encode.Value
    | RequestJson


update : Msg -> Scan -> ( Scan, Cmd Msg )
update msg scan =
    case msg of
        ChangeScanType newValue ->
            ( { scan | scan_type = newValue }, Cmd.none )

        UpdateInstruments jsonValue ->
            case Instrument.decoder jsonValue of
                Err err ->
                    ( { scan_type = err, instruments = [] }, Cmd.none )

                Ok new ->
                    ( { scan | instruments = updateInstruments new scan.instruments }
                    , Cmd.none
                    )

        RequestJson ->
            ( scan, requestJson "scan" )



-------------------
-- SUBSCRIPTIONS --
-------------------


subscriptions : Scan -> Sub Msg
subscriptions scan =
    jsonData UpdateInstruments



-------------
-- HELPERS --
-------------


{-| Replaces all instruments matching the module name with the instruments in
the new list.
-}
updateInstruments : List Instrument -> List Instrument -> List Instrument
updateInstruments newData oldData =
    case head newData of
        Nothing ->
            oldData

        Just data ->
            if data.class_name == "None" then
                filter (notModule data.module_name) oldData
            else
                newData ++ filter (notModule data.module_name) oldData


notModule : String -> Instrument -> Bool
notModule moduleName instrument =
    moduleName /= instrument.module_name



----------
-- MAIN --
----------


main : Program Never Scan Msg
main =
    Html.program
        { init = ( { scan_type = "None", instruments = [] }, Cmd.none )
        , view = view
        , update = update
        , subscriptions = subscriptions
        }
