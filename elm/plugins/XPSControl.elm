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


main =
    Html.program
        { init = ( default "None", Cmd.none )
        , view = view
        , update = update
        , subscriptions = \_ -> Sub.none
        }



--------------------
-- MAIN HTML VIEW --
--------------------


{-| Presents the configuration options for stage movement using the XPS Controller.

All HTML is presented in a div node, for use in the PLACE webapp.
-}
view : Stage -> Html Msg
view stage =
    Html.div [] <|
        Html.h2 [] [ Html.text "XPS-controlled stages" ]
            :: nameView stage


nameView : Stage -> List (Html Msg)
nameView stage =
    [ Html.text "Name: "
    , Html.select [ Html.Events.onInput ChangeName ]
        [ anOption stage.name "None" "None"
        , anOption stage.name "ShortStage" "Short stage"
        , anOption stage.name "LongStage" "Long stage"
        ]
    ]
        ++ (if stage.name == "None" then
                []
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
        [ Html.Attributes.value <| toString stage.start
        , Html.Attributes.type_ "number"
        , Html.Attributes.step "0.001"
        , Html.Events.onInput ChangeStart
        ]
        []
    ]


inputIncrement : Stage -> List (Html Msg)
inputIncrement stage =
    [ Html.br [] []
    , Html.text "Increment: "
    , Html.input
        [ Html.Attributes.value <| toString stage.increment
        , Html.Attributes.type_ "number"
        , Html.Attributes.step "0.001"
        , Html.Events.onInput ChangeIncrement
        ]
        []
    ]



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
    , start : Float
    , increment : Float
    }



--------------
-- MESSAGES --
--------------


type Msg
    = ChangeName String
    | ChangePriority String
    | ChangeStart String
    | ChangeIncrement String
    | SendJson


update : Msg -> Stage -> ( Stage, Cmd Msg )
update msg stage =
    case msg of
        ChangeName newValue ->
            update SendJson <| default newValue

        ChangePriority newValue ->
            update SendJson { stage | priority = withDefault 20 <| String.toInt newValue }

        ChangeStart newValue ->
            update SendJson { stage | start = withDefault 0.0 <| String.toFloat newValue }

        ChangeIncrement newValue ->
            update SendJson { stage | increment = withDefault 0.5 <| String.toFloat newValue }

        SendJson ->
            ( stage, jsonData <| toJson stage )


port jsonData : Json.Encode.Value -> Cmd msg


toJson : Stage -> Json.Encode.Value
toJson stage =
    Json.Encode.list
        [ Json.Encode.object
            [ ( "module_name", Json.Encode.string "xps_control" )
            , ( "class_name", Json.Encode.string stage.name )
            , ( "priority", Json.Encode.int stage.priority )
            , ( "config"
              , Json.Encode.object
                    [ ( "start", Json.Encode.float stage.start )
                    , ( "increment", Json.Encode.float stage.increment )
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
            , start = 0.0
            , increment = 0.5
            }

        otherwise ->
            { name = name
            , priority = 20
            , start = 0.0
            , increment = 0.5
            }


{-| Helper function to present an option in a drop-down selection box.
-}
anOption : String -> String -> String -> Html Msg
anOption str val disp =
    Html.option
        [ Html.Attributes.value val, Html.Attributes.selected (str == val) ]
        [ Html.text disp ]
