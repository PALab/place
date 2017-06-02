port module NewFocus exposing (view)

{-| The New Focus interface for PLACE.

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



--------------------
-- MAIN HTML VIEW --
--------------------


{-| Presents the configuration options for picomotor movement using the New
Focus Controller.

All HTML is presented in a div node, for use in the PLACE webapp.
-}
view : Picomotors -> Html Msg
view motors =
    Html.div [] <| mainView motors


mainView motors =
    Html.h2 [] [ Html.text "New Focus picomotors" ]
        :: Html.p [] (checkActiveView motors)
        :: if motors.active then
            [ Html.p [] <| inputPriority motors
            , Html.p [] <| inputXStart motors
            , Html.p [] <| inputYStart motors
            , Html.p [] <| inputXIncrement motors
            , Html.p [] <| inputYIncrement motors
            , Html.p [] <| inputMirrorDistance motors
            , Html.p [] <| sleepView motors
            , Html.p [] <| plotView motors
            ]
           else
            []


checkActiveView motors =
    [ Html.text "Active "
    , Html.input [ Html.Attributes.type_ "checkbox", Html.Events.onClick ToggleMotors ] []
    ]


inputPriority motors =
    [ Html.br [] []
    , Html.text "Priority: "
    , Html.input
        [ Html.Attributes.value <| toString motors.priority
        , Html.Attributes.type_ "number"
        , Html.Events.onInput ChangePriority
        ]
        []
    ]


inputXStart motors =
    [ Html.text "x-start: "
    , Html.input
        [ Html.Attributes.value <| toString motors.xstart
        , Html.Attributes.type_ "number"
        , Html.Attributes.step "0.001"
        , Html.Events.onInput ChangeXStart
        ]
        []
    ]


inputYStart motors =
    [ Html.text "y-start: "
    , Html.input
        [ Html.Attributes.value <| toString motors.ystart
        , Html.Attributes.type_ "number"
        , Html.Attributes.step "0.001"
        , Html.Events.onInput ChangeYStart
        ]
        []
    ]


inputXIncrement motors =
    [ Html.text "x-increment: "
    , Html.input
        [ Html.Attributes.value <| toString motors.xincrement
        , Html.Attributes.type_ "number"
        , Html.Attributes.step "0.001"
        , Html.Events.onInput ChangeXIncrement
        ]
        []
    ]


inputYIncrement motors =
    [ Html.text "y-increment: "
    , Html.input
        [ Html.Attributes.value <| toString motors.yincrement
        , Html.Attributes.type_ "number"
        , Html.Attributes.step "0.001"
        , Html.Events.onInput ChangeYIncrement
        ]
        []
    ]


inputMirrorDistance motors =
    [ Html.text "mirror distance: "
    , Html.input
        [ Html.Attributes.value <| toString motors.mirror
        , Html.Attributes.type_ "number"
        , Html.Attributes.step "0.001"
        , Html.Events.onInput ChangeMirrorDistance
        ]
        []
    ]


sleepView motors =
    [ Html.text "Sleep: "
    , Html.input
        [ Html.Attributes.value <| toString motors.sleep
        , Html.Attributes.type_ "number"
        , Html.Attributes.step "0.001"
        , Html.Events.onInput ChangeSleep
        ]
        []
    ]


plotView motors =
    [ Html.text "Plot: "
    , Html.select [ Html.Events.onInput PlotSwitch ]
        [ Html.option
            [ Html.Attributes.value "No"
            , Html.Attributes.selected (not motors.plot)
            ]
            [ Html.text "No" ]
        , Html.option
            [ Html.Attributes.value "Yes"
            , Html.Attributes.selected motors.plot
            ]
            [ Html.text "Yes" ]
        ]
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
type alias Picomotors =
    { active : Bool
    , priority : Int
    , xstart : Float
    , ystart : Float
    , xincrement : Float
    , yincrement : Float
    , mirror : Float
    , plot : Bool
    , sleep : Float
    }


default : Picomotors
default =
    { active = False
    , priority = 20
    , xstart = 0.0
    , ystart = 0.0
    , xincrement = 0.5
    , yincrement = 0.5
    , mirror = 10.0
    , plot = False
    , sleep = 0.5
    }



--------------
-- MESSAGES --
--------------


type Msg
    = ToggleMotors
    | ChangePriority String
    | ChangeXStart String
    | ChangeYStart String
    | ChangeXIncrement String
    | ChangeYIncrement String
    | ChangeMirrorDistance String
    | ChangeSleep String
    | PlotSwitch String
    | SendJson


update : Msg -> Picomotors -> ( Picomotors, Cmd Msg )
update msg motors =
    case msg of
        ToggleMotors ->
            update SendJson <| { motors | active = not motors.active }

        ChangePriority newValue ->
            update SendJson { motors | priority = withDefault 20 <| String.toInt newValue }

        ChangeXStart newValue ->
            update SendJson { motors | xstart = withDefault 0.0 <| String.toFloat newValue }

        ChangeYStart newValue ->
            update SendJson { motors | ystart = withDefault 0.0 <| String.toFloat newValue }

        ChangeXIncrement newValue ->
            update SendJson
                { motors
                    | xincrement =
                        withDefault 0.5 <|
                            String.toFloat newValue
                }

        ChangeYIncrement newValue ->
            update SendJson
                { motors
                    | yincrement =
                        withDefault 0.5 <|
                            String.toFloat newValue
                }

        ChangeMirrorDistance newValue ->
            update SendJson { motors | mirror = withDefault 10.0 <| String.toFloat newValue }

        ChangeSleep newValue ->
            update SendJson { motors | sleep = withDefault 0.5 <| String.toFloat newValue }

        PlotSwitch yesOrNo ->
            update SendJson { motors | plot = (yesOrNo == "Yes") }

        SendJson ->
            ( motors, jsonData <| toJson motors )


port jsonData : Json.Encode.Value -> Cmd msg


toJson : Picomotors -> Json.Encode.Value
toJson motors =
    Json.Encode.list
        [ Json.Encode.object
            [ ( "module_name", Json.Encode.string "new_focus" )
            , ( "class_name"
              , Json.Encode.string
                    (if motors.active then
                        "Picomotor"
                     else
                        "None"
                    )
              )
            , ( "priority", Json.Encode.int motors.priority )
            , ( "config"
              , Json.Encode.object
                    [ ( "x_start", Json.Encode.float motors.xstart )
                    , ( "y_start", Json.Encode.float motors.ystart )
                    , ( "x_increment", Json.Encode.float motors.xincrement )
                    , ( "y_increment", Json.Encode.float motors.yincrement )
                    , ( "mirror_distance", Json.Encode.float motors.mirror )
                    , ( "sleep_time", Json.Encode.float motors.sleep )
                    , ( "plot", Json.Encode.bool motors.plot )
                    ]
              )
            ]
        ]
