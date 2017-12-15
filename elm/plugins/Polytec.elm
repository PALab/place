port module Polytec exposing (view)

{-| The Polytec interface for PLACE.

# Main HTML view

@docs view

-}

import Html exposing (Html)
import Html.Attributes
import Html.Events
import Json.Encode
import Result exposing (withDefault)
import ModuleHelpers exposing (..)


main =
    Html.program
        { init = ( default, Cmd.none )
        , view = \model -> Html.div [] (view model)
        , update = update
        , subscriptions = \_ -> Sub.none
        }


type alias Vibrometer =
    { active : Bool
    , priority : Int
    , dd300 : Bool
    , dd900 : Bool
    , vd08 : Bool
    , vd09 : Bool
    , dd300range : String
    , dd900range : String
    , vd08range : String
    , vd09range : String
    , timeout : String
    , autofocus : String
    , autofocusEverytime : Bool
    }


default : Vibrometer
default =
    { active = False
    , priority = 50
    , dd300 = False
    , dd900 = False
    , vd08 = False
    , vd09 = False
    , dd300range = dd300rangeDefault
    , dd900range = dd900rangeDefault
    , vd08range = vd08rangeDefault
    , vd09range = vd09rangeDefault
    , timeout = "30.0"
    , autofocus = "none"
    , autofocusEverytime = False
    }


dd300rangeDefault =
    "50nm/V"


dd900rangeDefault =
    "5mm/s/V"


vd08rangeDefault =
    "5mm/s/V"


vd09rangeDefault =
    "5mm/s/V"



--------------------
-- MAIN HTML VIEW --
--------------------


view : Vibrometer -> List (Html Msg)
view vib =
    title "Polytec vibrometer" vib.active ToggleActive Close
        ++ if vib.active then
            selectDecoders vib
                :: if vib.dd300 || vib.dd900 || vib.vd08 || vib.vd09 then
                    inputPriority vib
                        :: inputRange vib
                        ++ [ selectAutofocus vib ]
                   else
                    [ Html.text "" ]
           else
            [ Html.text "" ]


selectDecoders : Vibrometer -> Html Msg
selectDecoders vib =
    Html.p []
        [ Html.text "Decoders: DD-300 "
        , Html.input [ Html.Attributes.type_ "checkbox", Html.Events.onClick ToggleDD300 ] []
        , Html.text " | DD-900 "
        , Html.input [ Html.Attributes.type_ "checkbox", Html.Events.onClick ToggleDD900 ] []
        , Html.text " | VD-08 "
        , Html.input [ Html.Attributes.type_ "checkbox", Html.Events.onClick ToggleVD08 ] []
        , Html.text " | VD-09 "
        , Html.input [ Html.Attributes.type_ "checkbox", Html.Events.onClick ToggleVD09 ] []
        ]


inputPriority : Vibrometer -> Html Msg
inputPriority vib =
    Html.p []
        [ Html.text "Priority: "
        , Html.input
            [ Html.Attributes.value <| toString vib.priority
            , Html.Attributes.type_ "number"
            , Html.Events.onInput ChangePriority
            ]
            []
        ]


inputRange : Vibrometer -> List (Html Msg)
inputRange vib =
    []
        ++ (if vib.dd300 then
                [ Html.p [] [ Html.text "DD-300 range: 50 nm/V" ]
                ]
            else
                [ Html.text "" ]
           )
        ++ (if vib.dd900 then
                [ Html.p []
                    [ Html.text "DD-900 range: "
                    , Html.select [ Html.Events.onInput ChangeDD900Range ]
                        [ anOption vib.dd900range "5mm/V" "5 mm/V"
                        , anOption vib.dd900range "2mm/V" "2 mm/V"
                        , anOption vib.dd900range "1mm/V" "1 mm/V"
                        , anOption vib.dd900range "500um/V" "500 um/V"
                        , anOption vib.dd900range "200um/V" "200 um/V"
                        , anOption vib.dd900range "100um/V" "100 um/V"
                        , anOption vib.dd900range "50um/V" "50 um/V"
                        , anOption vib.dd900range "20um/V" "20 um/V"
                        , anOption vib.dd900range "10um/V" "10 um/V"
                        , anOption vib.dd900range "5um/V" "5 um/V"
                        , anOption vib.dd900range "2um/V" "2 um/V"
                        , anOption vib.dd900range "1um/V" "1 um/V"
                        , anOption vib.dd900range "500nm/V" "500 nm/V"
                        , anOption vib.dd900range "200nm/V" "200 nm/V"
                        , anOption vib.dd900range "100nm/V" "100 nm/V"
                        , anOption vib.dd900range "50nm/V" "50 nm/V"
                        ]
                    ]
                ]
            else
                []
           )
        ++ (if vib.vd08 then
                [ Html.p []
                    [ Html.text "VD-08 range: "
                    , Html.select [ Html.Events.onInput ChangeVD08Range ]
                        [ anOption vib.vd08range "50mm/s/V" "50 mm/s/V"
                        , anOption vib.vd08range "20mm/s/V" "20 mm/s/V"
                        , anOption vib.vd08range "10mm/s/V" "10 mm/s/V"
                        , anOption vib.vd08range "5mm/s/V" "5 mm/s/V"
                        , anOption vib.vd08range "2mm/s/V" "2 mm/s/V"
                        , anOption vib.vd08range "1mm/s/V" "1 mm/s/V"
                        , anOption vib.vd08range "0.5mm/s/V" "0.5 mm/s/V"
                        , anOption vib.vd08range "0.2mm/s/V" "0.2 mm/s/V"
                        ]
                    ]
                ]
            else
                []
           )
        ++ (if vib.vd09 then
                [ Html.p []
                    [ Html.text "VD-09 range: "
                    , Html.select [ Html.Events.onInput ChangeVD09Range ]
                        [ anOption vib.vd09range "1m/s/V" "1 m/s/V"
                        , anOption vib.vd09range "1m/s/V LP" "1 m/s/V LP"
                        , anOption vib.vd09range "500mm/s/V" "500 mm/s/V"
                        , anOption vib.vd09range "500mm/s/V LP" "500 mm/s/V LP"
                        , anOption vib.vd09range "200mm/s/V" "200 mm/s/V"
                        , anOption vib.vd09range "200mm/s/V LP" "200 mm/s/V LP"
                        , anOption vib.vd09range "100mm/s/V" "100 mm/s/V"
                        , anOption vib.vd09range "100mm/s/V LP" "100 mm/s/V LP"
                        , anOption vib.vd09range "50mm/s/V" "50 mm/s/V"
                        , anOption vib.vd09range "50mm/s/V LP" "50 mm/s/V LP"
                        , anOption vib.vd09range "20mm/s/V" "20 mm/s/V"
                        , anOption vib.vd09range "20mm/s/V LP" "20 mm/s/V LP"
                        , anOption vib.vd09range "10mm/s/V" "10 mm/s/V"
                        , anOption vib.vd09range "5mm/s/V" "5 mm/s/V"
                        ]
                    ]
                ]
            else
                []
           )


selectAutofocus : Vibrometer -> Html Msg
selectAutofocus vib =
    Html.p [] <|
        [ Html.text "Autofocus: "
        , Html.select [ Html.Events.onInput ChangeAutofocus ]
            [ Html.option
                [ Html.Attributes.value "none"
                , Html.Attributes.selected (vib.autofocus == "none")
                ]
                [ Html.text "None" ]
            , Html.option
                [ Html.Attributes.value "short"
                , Html.Attributes.selected (vib.autofocus == "short")
                ]
                [ Html.text "Short" ]
            , Html.option
                [ Html.Attributes.value "medium"
                , Html.Attributes.selected (vib.autofocus == "medium")
                ]
                [ Html.text "Medium" ]
            , Html.option
                [ Html.Attributes.value "full"
                , Html.Attributes.selected (vib.autofocus == "full")
                ]
                [ Html.text "Full" ]
            ]
        ]
            ++ (if vib.autofocus /= "none" then
                    ([ Html.text " On every update "
                     , Html.input
                        [ Html.Attributes.type_ "checkbox"
                        , Html.Events.onClick ToggleEverytime
                        ]
                        []
                     , Html.text " Timeout: "
                     , Html.input
                        [ Html.Attributes.value vib.timeout
                        , Html.Events.onInput ChangeTimeout
                        ]
                        []
                     ]
                        ++ (case String.toFloat vib.timeout of
                                Err errorMsg ->
                                    [ Html.br [] []
                                    , Html.span [ Html.Attributes.class "error-text" ]
                                        [ Html.text (" Error: " ++ errorMsg) ]
                                    ]

                                otherwise ->
                                    []
                           )
                    )
                else
                    []
               )



--------------
-- MESSAGES --
--------------


type Msg
    = ToggleActive
    | ToggleDD300
    | ToggleDD900
    | ToggleVD08
    | ToggleVD09
    | ChangePriority String
    | ChangeDD900Range String
    | ChangeVD08Range String
    | ChangeVD09Range String
    | ChangeTimeout String
    | ChangeAutofocus String
    | ToggleEverytime
    | SendJson
    | Close


update : Msg -> Vibrometer -> ( Vibrometer, Cmd Msg )
update msg vib =
    case msg of
        ToggleActive ->
            if vib.active then
                update SendJson default
            else
                update SendJson { default | active = True }

        ToggleDD300 ->
            update SendJson { vib | dd300 = not vib.dd300, dd300range = dd300rangeDefault }

        ToggleDD900 ->
            update SendJson { vib | dd900 = not vib.dd900, dd900range = dd900rangeDefault }

        ToggleVD08 ->
            update SendJson { vib | vd08 = not vib.vd08, vd08range = vd08rangeDefault }

        ToggleVD09 ->
            update SendJson { vib | vd09 = not vib.vd09, vd09range = vd09rangeDefault }

        ChangePriority newValue ->
            update SendJson { vib | priority = withDefault 50 <| String.toInt newValue }

        ChangeDD900Range newValue ->
            update SendJson { vib | dd900range = newValue }

        ChangeVD08Range newValue ->
            update SendJson { vib | vd08range = newValue }

        ChangeVD09Range newValue ->
            update SendJson { vib | vd09range = newValue }

        ChangeTimeout newValue ->
            update SendJson { vib | timeout = newValue }

        ChangeAutofocus newValue ->
            update SendJson { vib | autofocus = newValue }

        ToggleEverytime ->
            update SendJson { vib | autofocusEverytime = not vib.autofocusEverytime }

        SendJson ->
            ( vib, jsonData <| toJson vib )

        Close ->
            let
                ( clearInstrument, sendJsonCmd ) =
                    update SendJson <| default
            in
                clearInstrument ! [ sendJsonCmd, removeModule "polytec" ]


port jsonData : Json.Encode.Value -> Cmd msg


port removeModule : String -> Cmd msg


toJson : Vibrometer -> Json.Encode.Value
toJson vib =
    Json.Encode.list
        [ Json.Encode.object
            [ ( "module_name", Json.Encode.string "polytec" )
            , ( "class_name"
              , Json.Encode.string
                    (if vib.dd300 || vib.dd900 || vib.vd08 || vib.vd09 then
                        "Vibrometer"
                     else
                        "None"
                    )
              )
            , ( "priority", Json.Encode.int vib.priority )
            , ( "data_register", Json.Encode.list (List.map Json.Encode.string []) )
            , ( "config"
              , Json.Encode.object
                    [ ( "dd_300", Json.Encode.bool vib.dd300 )
                    , ( "dd_900", Json.Encode.bool vib.dd900 )
                    , ( "vd_08", Json.Encode.bool vib.vd08 )
                    , ( "vd_09", Json.Encode.bool vib.vd09 )
                    , ( "dd_300_range", Json.Encode.string vib.dd300range )
                    , ( "dd_900_range", Json.Encode.string vib.dd900range )
                    , ( "vd_08_range", Json.Encode.string vib.vd08range )
                    , ( "vd_09_range", Json.Encode.string vib.vd09range )
                    , ( "timeout"
                      , Json.Encode.float
                            (case String.toFloat vib.timeout of
                                Ok num ->
                                    num

                                otherwise ->
                                    -1.0
                            )
                      )
                    , ( "autofocus", Json.Encode.string vib.autofocus )
                    , ( "autofocus_everytime", Json.Encode.bool vib.autofocusEverytime )
                    ]
              )
            ]
        ]


{-| Helper function to present an option in a drop-down selection box.
-}
anOption : String -> String -> String -> Html Msg
anOption str val disp =
    Html.option
        [ Html.Attributes.value val, Html.Attributes.selected (str == val) ]
        [ Html.text disp ]
