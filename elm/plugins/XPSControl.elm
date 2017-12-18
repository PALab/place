port module XPSControl exposing (main)

import Html exposing (Html)
import Html.Events
import Html.Attributes
import Json.Encode
import Result exposing (withDefault)
import ModuleHelpers


pythonModuleName =
    "xps_control"


type alias Stage =
    { name : String
    , priority : Int
    , active : Bool
    , start : String
    , increment : String
    , end : String
    }


defaultModel : Stage
defaultModel =
    { name = "None"
    , priority = 20
    , active = False
    , start = "0.0"
    , increment = "0.5"
    , end = "calculate"
    }


type Msg
    = ToggleActive
    | ChangeName String
    | ChangePriority String
    | ChangeStart String
    | ChangeIncrement String
    | ChangeEnd String
    | SendJson
    | Close


port jsonData : Json.Encode.Value -> Cmd msg


port removeModule : String -> Cmd msg


update : Msg -> Stage -> ( Stage, Cmd Msg )
update msg stage =
    case msg of
        ToggleActive ->
            if stage.active then
                update SendJson <| defaultModel
            else
                update SendJson { stage | active = True }

        ChangeName newValue ->
            update SendJson { stage | name = newValue }

        ChangePriority newValue ->
            update SendJson { stage | priority = withDefault 20 <| String.toInt newValue }

        ChangeStart newValue ->
            update SendJson { stage | start = newValue }

        ChangeIncrement newValue ->
            update SendJson { stage | increment = newValue, end = "calculate" }

        ChangeEnd newValue ->
            update SendJson { stage | increment = "calculate", end = newValue }

        SendJson ->
            ( stage, jsonData <| toJson stage )

        Close ->
            let
                ( clearInstrument, sendJsonCmd ) =
                    update SendJson <| defaultModel
            in
                clearInstrument ! [ sendJsonCmd, removeModule "xps_control" ]


main =
    Html.program
        { init = ( defaultModel, Cmd.none )
        , view = \stage -> Html.div [] (view stage)
        , update = update
        , subscriptions = \_ -> Sub.none
        }


view : Stage -> List (Html Msg)
view stage =
    ModuleHelpers.title "XPS-controlled stages" stage.active ToggleActive Close
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
                    inputPriority stage
                        ++ inputStart stage
                        ++ inputIncrement stage
                        ++ inputEnd stage
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
        ++ if stage.increment == "calculate" then
            [ Html.text "" ]
           else
            (case String.toFloat stage.increment of
                Err errorMsg ->
                    [ Html.br [] []
                    , Html.span [ Html.Attributes.class "error-text" ]
                        [ Html.text (" Error: " ++ errorMsg) ]
                    ]

                otherwise ->
                    [ Html.text "" ]
            )


inputEnd : Stage -> List (Html Msg)
inputEnd stage =
    [ Html.br [] []
    , Html.text "End: "
    , Html.input
        [ Html.Attributes.value stage.end
        , Html.Events.onInput ChangeEnd
        ]
        []
    ]
        ++ if stage.end == "calculate" then
            [ Html.text "" ]
           else
            (case String.toFloat stage.end of
                Err errorMsg ->
                    [ Html.br [] []
                    , Html.span [ Html.Attributes.class "error-text" ]
                        [ Html.text (" Error: " ++ errorMsg) ]
                    ]

                otherwise ->
                    [ Html.text "" ]
            )


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
                    , if stage.end == "calculate" then
                        ( "increment"
                        , Json.Encode.float
                            (case String.toFloat stage.increment of
                                Ok num ->
                                    num

                                otherwise ->
                                    1.0
                            )
                        )
                      else
                        ( "end"
                        , Json.Encode.float
                            (case String.toFloat stage.end of
                                Ok num ->
                                    num

                                otherwise ->
                                    1.0
                            )
                        )
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
