port module NewFocus exposing (main)

import Html exposing (Html)
import Html.Attributes
import Html.Events
import Json.Encode
import Result exposing (withDefault)
import ModuleHelpers exposing (..)


main =
    Html.program
        { init = ( default, Cmd.none )
        , view = \motors -> Html.div [] (view motors)
        , update = update
        , subscriptions = \_ -> Sub.none
        }


view : Picomotors -> List (Html Msg)
view motors =
    title "New Focus picomotors" motors.active ToggleActive Close
        ++ if motors.active then
            selectShape motors
                :: if motors.shape /= "none" then
                    inputPriority motors
                        :: inputShape motors
                        :: sleepView motors
                        :: plotView motors
                        :: []
                   else
                    [ Html.text "" ]
           else
            [ Html.text "" ]


selectShape motors =
    Html.p [] <|
        [ Html.text "Shape: "
        , Html.select [ Html.Events.onInput ChangeShape ]
            [ ModuleHelpers.anOption motors.shape ( "none", "None" )
            , ModuleHelpers.anOption motors.shape ( "point", "Point" )
            , ModuleHelpers.anOption motors.shape ( "line", "Line" )
            , ModuleHelpers.anOption motors.shape ( "circle", "Circle" )
            , ModuleHelpers.anOption motors.shape ( "arc", "Arc" )
            ]
        ]


inputPriority motors =
    Html.p [] <|
        [ Html.text "Priority: "
        , Html.input
            [ Html.Attributes.value <| toString motors.priority
            , Html.Attributes.type_ "number"
            , Html.Events.onInput ChangePriority
            ]
            []
        ]


inputShape motors =
    case motors.shape of
        "point" ->
            Html.p [] <|
                []
                    ++ inputXOne motors
                    ++ [ Html.br [] [] ]
                    ++ inputYOne motors

        "line" ->
            Html.p [] <|
                []
                    ++ inputXOne motors
                    ++ [ Html.br [] [] ]
                    ++ inputYOne motors
                    ++ [ Html.br [] [] ]
                    ++ inputXTwo motors
                    ++ [ Html.br [] [] ]
                    ++ inputYTwo motors

        "circle" ->
            Html.p [] <|
                []
                    ++ inputXOne motors
                    ++ [ Html.br [] [] ]
                    ++ inputYOne motors
                    ++ [ Html.br [] [] ]
                    ++ inputRadius motors

        "arc" ->
            Html.p [] <|
                []
                    ++ inputXOne motors
                    ++ [ Html.br [] [] ]
                    ++ inputYOne motors
                    ++ [ Html.br [] [] ]
                    ++ inputRadius motors
                    ++ [ Html.br [] [] ]
                    ++ inputSectors motors
                    ++ [ Html.br [] [] ]
                    ++ inputStartingSector motors

        otherwise ->
            Html.text ""


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


inputRadius motors =
    [ Html.text "radius: "
    , Html.input
        [ Html.Attributes.value <| toString motors.radius
        , Html.Attributes.type_ "number"
        , Html.Events.onInput ChangeRadius
        ]
        []
    ]


inputSectors motors =
    [ Html.text "circle sectors: "
    , Html.input
        [ Html.Attributes.value <| toString motors.sectors
        , Html.Attributes.type_ "number"
        , Html.Events.onInput ChangeSectors
        ]
        []
    ]


inputStartingSector motors =
    [ Html.text "starting sector: "
    , Html.input
        [ Html.Attributes.value <| toString motors.startingSector
        , Html.Attributes.type_ "number"
        , Html.Events.onInput ChangeStartingSector
        ]
        []
    ]


sleepView motors =
    Html.p [] <|
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
    , shape : String
    , priority : Int
    , xone : Int
    , yone : Int
    , xtwo : Int
    , ytwo : Int
    , radius : Int
    , sectors : Int
    , startingSector : Int
    , plot : Bool
    , invertX : Bool
    , invertY : Bool
    , sleep : Float
    }


default : Picomotors
default =
    { active = False
    , shape = "none"
    , priority = 20
    , xone = 0
    , yone = 0
    , xtwo = 0
    , ytwo = 0
    , radius = 0
    , sectors = 360
    , startingSector = 0
    , plot = False
    , invertX = True
    , invertY = True
    , sleep = 0.5
    }



--------------
-- MESSAGES --
--------------


type Msg
    = ToggleActive
    | ChangeShape String
    | ChangePriority String
    | ChangeXOne String
    | ChangeYOne String
    | ChangeXTwo String
    | ChangeYTwo String
    | ChangeRadius String
    | ChangeSectors String
    | ChangeStartingSector String
    | ChangeSleep String
    | PlotSwitch String
    | ToggleInvertX
    | ToggleInvertY
    | SendJson
    | Close


update : Msg -> Picomotors -> ( Picomotors, Cmd Msg )
update msg motors =
    case msg of
        ToggleActive ->
            if motors.active then
                update SendJson default
            else
                update SendJson { motors | active = True }

        ChangeShape newValue ->
            update SendJson <| { motors | shape = newValue }

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

        ChangeRadius newValue ->
            update SendJson { motors | radius = withDefault 0 <| String.toInt newValue }

        ChangeSectors newValue ->
            update SendJson { motors | sectors = withDefault 360 <| String.toInt newValue }

        ChangeStartingSector newValue ->
            update SendJson
                { motors
                    | startingSector = withDefault 0 <| String.toInt newValue
                }

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

        Close ->
            let
                ( clearInstrument, sendJsonCmd ) =
                    update SendJson <| default
            in
                clearInstrument ! [ sendJsonCmd, removeModule "new_focus" ]


port jsonData : Json.Encode.Value -> Cmd msg


port removeModule : String -> Cmd msg


toJson : Picomotors -> Json.Encode.Value
toJson motors =
    Json.Encode.list
        [ Json.Encode.object
            [ ( "module_name", Json.Encode.string "new_focus" )
            , ( "class_name"
              , Json.Encode.string
                    (if motors.shape == "none" then
                        "None"
                     else
                        "Picomotor"
                    )
              )
            , ( "priority", Json.Encode.int motors.priority )
            , ( "data_register"
              , Json.Encode.list
                    (List.map Json.Encode.string
                        [ "Picomotors-x_position", "Picomotors-y_position" ]
                    )
              )
            , ( "config"
              , Json.Encode.object
                    [ ( "shape", Json.Encode.string motors.shape )
                    , ( "x_one", Json.Encode.int motors.xone )
                    , ( "y_one", Json.Encode.int motors.yone )
                    , ( "x_two", Json.Encode.int motors.xtwo )
                    , ( "y_two", Json.Encode.int motors.ytwo )
                    , ( "radius", Json.Encode.int motors.radius )
                    , ( "sectors", Json.Encode.int motors.sectors )
                    , ( "starting_sector", Json.Encode.int motors.startingSector )
                    , ( "sleep_time", Json.Encode.float motors.sleep )
                    , ( "plot", Json.Encode.bool motors.plot )
                    , ( "invert_x", Json.Encode.bool motors.invertX )
                    , ( "invert_y", Json.Encode.bool motors.invertY )
                    ]
              )
            ]
        ]
