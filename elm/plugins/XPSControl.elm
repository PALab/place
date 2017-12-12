port module XPSControl exposing (view)

{-| The XPS controller interface for PLACE.

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
        { init = ( default "None", Cmd.none )
        , view = \stage -> Html.div [] (view stage)
        , update = update
        , subscriptions = \_ -> Sub.none
        }


view : Stage -> List (Html Msg)
view stage =
    title "XPS-controlled stages" stage.active ToggleActive Close
        ++ if stage.active then
            [ nameView stage ]
           else
            [ Html.text "" ]


nameView : Stage -> Html Msg
nameView stage =
    Html.p [] <|
        [ Html.text "Name: "
        , Html.select [ Html.Events.onInput ChangeName ]
            [ anOption stage.name "None" "None"
            , anOption stage.name "ShortStage" "Short linear stage"
            , anOption stage.name "LongStage" "Long linear stage"
            , anOption stage.name "RotStage" "Rotational stage"
            ]
        ]
            ++ (if stage.name == "None" then
                    [ Html.text "" ]
                else
                    inputPriority stage ++ inputStart stage ++ inputIncrement stage
               )


inputPriority : Stage -> List (Html Msg)
inputPriority stage =
    [ Html.br [] []
    , Html.text "Priority: "
    , Html.input
        [ Html.Attributes.value <| toString stage.priority
        , Html.Attributes.type_ "number"
        , Html.Events.onInput ChangePriority
        ]
        []
    ]


inputStart : Stage -> List (Html Msg)
inputStart stage =
    [ Html.br [] []
    , Html.text "Start: "
    , Html.input
        [ Html.Attributes.value stage.start
        , Html.Events.onInput ChangeStart
        ]
        []
    ]
        ++ (case String.toFloat stage.start of
                Err errorMsg ->
                    [ Html.br [] []
                    , Html.span [ Html.Attributes.class "error-text" ]
                        [ Html.text (" Error: " ++ errorMsg) ]
                    ]

                otherwise ->
                    [ Html.text "" ]
           )


inputIncrement : Stage -> List (Html Msg)
inputIncrement stage =
    [ Html.br [] []
    , Html.text "Increment: "
    , Html.input
        [ Html.Attributes.value stage.increment
        , Html.Events.onInput ChangeIncrement
        ]
        []
    ]
        ++ (case String.toFloat stage.increment of
                Err errorMsg ->
                    [ Html.br [] []
                    , Html.span [ Html.Attributes.class "error-text" ]
                        [ Html.text (" Error: " ++ errorMsg) ]
                    ]

                otherwise ->
                    [ Html.text "" ]
           )



-------------------
-- CONFIG RECORD --
-------------------


{-| All PLACE configurations must contain a "name" string, a "priority"
integer, and a "config" record. Specific values within "config" are not used by
PLACE.

The "name" should match the name of the Python Class written for the
instrument.

The "priority" value is the order in which the Scan will update the
instruments. Lower values will have the update method called before higher
values.

-}
type alias Stage =
    { name : String
    , priority : Int
    , active : Bool
    , start : String
    , increment : String
    }



--------------
-- MESSAGES --
--------------


type Msg
    = ToggleActive
    | ChangeName String
    | ChangePriority String
    | ChangeStart String
    | ChangeIncrement String
    | SendJson
    | Close


update : Msg -> Stage -> ( Stage, Cmd Msg )
update msg stage =
    case msg of
        ToggleActive ->
            if stage.active then
                update SendJson <| default "None"
            else
                update SendJson { stage | active = True }

        ChangeName newValue ->
            update SendJson <| default newValue

        ChangePriority newValue ->
            update SendJson { stage | priority = withDefault 20 <| String.toInt newValue }

        ChangeStart newValue ->
            update SendJson { stage | start = newValue }

        ChangeIncrement newValue ->
            update SendJson { stage | increment = newValue }

        SendJson ->
            ( stage, jsonData <| toJson stage )

        Close ->
            let
                ( clearInstrument, sendJsonCmd ) =
                    update SendJson <| default "None"
            in
                clearInstrument ! [ sendJsonCmd, removeInstrument "xps_control" ]


port jsonData : Json.Encode.Value -> Cmd msg


port removeInstrument : String -> Cmd msg


toJson : Stage -> Json.Encode.Value
toJson stage =
    Json.Encode.list
        [ Json.Encode.object
            [ ( "module_name", Json.Encode.string "xps_control" )
            , ( "class_name", Json.Encode.string stage.name )
            , ( "priority", Json.Encode.int stage.priority )
            , ( "data_register"
              , Json.Encode.list
                    (List.map Json.Encode.string [ stage.name ++ "-position" ])
              )
            , ( "config"
              , Json.Encode.object
                    [ ( "start"
                      , Json.Encode.float
                            (case String.toFloat stage.start of
                                Ok num ->
                                    num

                                otherwise ->
                                    0.0
                            )
                      )
                    , ( "increment"
                      , Json.Encode.float
                            (case String.toFloat stage.increment of
                                Ok num ->
                                    num

                                otherwise ->
                                    0.0
                            )
                      )
                    ]
              )
            ]
        ]


default : String -> Stage
default name =
    case name of
        "None" ->
            { name = "None"
            , priority = 20
            , active = False
            , start = "0.0"
            , increment = "0.5"
            }

        otherwise ->
            { name = name
            , priority = 20
            , active = True
            , start = "0.0"
            , increment = "0.5"
            }


{-| Helper function to present an option in a drop-down selection box.
-}
anOption : String -> String -> String -> Html Msg
anOption str val disp =
    Html.option
        [ Html.Attributes.value val, Html.Attributes.selected (str == val) ]
        [ Html.text disp ]
