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


main =
    Html.program
        { init = ( default, Cmd.none )
        , view = view
        , update = update
        , subscriptions = \_ -> Sub.none
        }


type alias Vibrometer =
    { priority : Int
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
    }


default : Vibrometer
default =
    { priority = 50
    , dd300 = False
    , dd900 = False
    , vd08 = False
    , vd09 = False
    , dd300range = dd300rangeDefault
    , dd900range = dd900rangeDefault
    , vd08range = vd08rangeDefault
    , vd09range = vd09rangeDefault
    , timeout = "6.25"
    , autofocus = "none"
    }


dd300rangeDefault =
    "5mm/s/V"


dd900rangeDefault =
    "5mm/s/V"


vd08rangeDefault =
    "5mm/s/V"


vd09rangeDefault =
    "5mm/s/V"



--------------------
-- MAIN HTML VIEW --
--------------------


view : Vibrometer -> Html Msg
view vib =
    Html.div [] <|
        [ Html.h2 [] [ Html.text "Polytec vibrometer" ]
        , selectDecoders vib
        ]
            ++ if vib.dd300 || vib.dd900 || vib.vd08 || vib.vd09 then
                inputPriority vib
                    :: inputRange vib
                    ++ [ selectAutofocus vib ]
               else
                []


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
                [ Html.p []
                    [ Html.text "DD-300 range: "
                    , Html.input
                        [ Html.Attributes.value vib.dd300range
                        , Html.Events.onInput ChangeDD300Range
                        ]
                        []
                    ]
                ]
            else
                []
           )
        ++ (if vib.dd900 then
                [ Html.p []
                    [ Html.text "DD-900 range: "
                    , Html.input
                        [ Html.Attributes.value vib.dd900range
                        , Html.Events.onInput ChangeDD900Range
                        ]
                        []
                    ]
                ]
            else
                []
           )
        ++ (if vib.vd08 then
                [ Html.p []
                    [ Html.text "VD-08 range: "
                    , Html.input
                        [ Html.Attributes.value vib.vd08range
                        , Html.Events.onInput ChangeVD08Range
                        ]
                        []
                    ]
                ]
            else
                []
           )
        ++ (if vib.vd09 then
                [ Html.p []
                    [ Html.text "VD-09 range: "
                    , Html.input
                        [ Html.Attributes.value vib.vd09range
                        , Html.Events.onInput ChangeVD09Range
                        ]
                        []
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
                    ([ Html.text " Timeout: "
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
    = ToggleDD300
    | ToggleDD900
    | ToggleVD08
    | ToggleVD09
    | ChangePriority String
    | ChangeDD300Range String
    | ChangeDD900Range String
    | ChangeVD08Range String
    | ChangeVD09Range String
    | ChangeTimeout String
    | ChangeAutofocus String
    | SendJson


update : Msg -> Vibrometer -> ( Vibrometer, Cmd Msg )
update msg vib =
    case msg of
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

        ChangeDD300Range newValue ->
            update SendJson { vib | dd300range = newValue }

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

        SendJson ->
            ( vib, jsonData <| toJson vib )


port jsonData : Json.Encode.Value -> Cmd msg


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
                    ]
              )
            ]
        ]
