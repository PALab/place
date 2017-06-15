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
            , Html.p [] <|
                inputXOne motors
                    ++ [ Html.br [] [] ]
                    ++ inputYOne motors
                    ++ [ Html.br [] [] ]
                    ++ inputXTwo motors
                    ++ [ Html.br [] [] ]
                    ++ inputYTwo motors
            , Html.p [] <| sleepView motors
            , plotView motors
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


inputXOne motors =
    [ Html.text "x-one: "
    , Html.input
        [ Html.Attributes.value <| toString motors.xone
        , Html.Attributes.type_ "number"
        , Html.Events.onInput ChangeXOne
        ]
        []
    ]


inputYOne motors =
    [ Html.text "y-one: "
    , Html.input
        [ Html.Attributes.value <| toString motors.yone
        , Html.Attributes.type_ "number"
        , Html.Events.onInput ChangeYOne
        ]
        []
    ]


inputXTwo motors =
    [ Html.text "x-two: "
    , Html.input
        [ Html.Attributes.value <| toString motors.xtwo
        , Html.Attributes.type_ "number"
        , Html.Events.onInput ChangeXTwo
        ]
        []
    ]


inputYTwo motors =
    [ Html.text "y-two: "
    , Html.input
        [ Html.Attributes.value <| toString motors.ytwo
        , Html.Attributes.type_ "number"
        , Html.Events.onInput ChangeYTwo
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
    Html.p [] <|
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
            ++ (if motors.plot then
                    [ Html.br [] []
                    , Html.text " Invert x: "
                    , Html.input
                        [ Html.Attributes.type_ "checkbox"
                        , Html.Attributes.checked motors.invertX
                        , Html.Events.onClick ToggleInvertX
                        ]
                        []
                    , Html.text " Invert y: "
                    , Html.input
                        [ Html.Attributes.type_ "checkbox"
                        , Html.Attributes.checked motors.invertY
                        , Html.Events.onClick ToggleInvertY
                        ]
                        []
                    ]
                else
                    []
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
type alias Picomotors =
    { active : Bool
    , priority : Int
    , xone : Int
    , yone : Int
    , xtwo : Int
    , ytwo : Int
    , plot : Bool
    , invertX : Bool
    , invertY : Bool
    , sleep : Float
    }


default : Picomotors
default =
    { active = False
    , priority = 20
    , xone = 0
    , yone = 0
    , xtwo = 0
    , ytwo = 0
    , plot = False
    , invertX = True
    , invertY = True
    , sleep = 0.5
    }



--------------
-- MESSAGES --
--------------


type Msg
    = ToggleMotors
    | ChangePriority String
    | ChangeXOne String
    | ChangeYOne String
    | ChangeXTwo String
    | ChangeYTwo String
    | ChangeSleep String
    | PlotSwitch String
    | ToggleInvertX
    | ToggleInvertY
    | SendJson


update : Msg -> Picomotors -> ( Picomotors, Cmd Msg )
update msg motors =
    case msg of
        ToggleMotors ->
            update SendJson <| { motors | active = not motors.active }

        ChangePriority newValue ->
            update SendJson { motors | priority = withDefault 20 <| String.toInt newValue }

        ChangeXOne newValue ->
            update SendJson { motors | xone = withDefault 0 <| String.toInt newValue }

        ChangeYOne newValue ->
            update SendJson { motors | yone = withDefault 0 <| String.toInt newValue }

        ChangeXTwo newValue ->
            update SendJson { motors | xtwo = withDefault 0 <| String.toInt newValue }

        ChangeYTwo newValue ->
            update SendJson { motors | ytwo = withDefault 0 <| String.toInt newValue }

        ChangeSleep newValue ->
            update SendJson { motors | sleep = withDefault 0.5 <| String.toFloat newValue }

        PlotSwitch yesOrNo ->
            update SendJson { motors | plot = (yesOrNo == "Yes") }

        ToggleInvertX ->
            update SendJson <| { motors | invertX = not motors.invertX }

        ToggleInvertY ->
            update SendJson <| { motors | invertY = not motors.invertY }

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
                    [ ( "x_one", Json.Encode.int motors.xone )
                    , ( "y_one", Json.Encode.int motors.yone )
                    , ( "x_two", Json.Encode.int motors.xtwo )
                    , ( "y_two", Json.Encode.int motors.ytwo )
                    , ( "sleep_time", Json.Encode.float motors.sleep )
                    , ( "plot", Json.Encode.bool motors.plot )
                    , ( "invert_x", Json.Encode.bool motors.invertX )
                    , ( "invert_y", Json.Encode.bool motors.invertY )
                    ]
              )
            ]
        ]
