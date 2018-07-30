port module XPSControl exposing (main)

import Html exposing (Html)
import Html.Events
import Html.Attributes
import Json.Encode
import Result exposing (withDefault)
import ModuleHelpers


attributions : ModuleHelpers.Attributions
attributions =
    { authors = [ "Paul Freeman" ]
    , maintainer = "Paul Freeman"
    , maintainerEmail = "pfre484@aucklanduni.ac.nz"
    }


pythonModuleName =
    "xps_control"


type alias Stage =
    { name : String
    , priority : String
    , active : Bool
    , mode : String
    , velocity : String
    , acceleration : String
    , wait : String
    , start : String
    , increment : String
    , end : String
    , progress : Maybe Json.Encode.Value
    }


defaultModel : Stage
defaultModel =
    { name = "None"
    , priority = "20"
    , active = False
    , mode = "incremental"
    , velocity = "500"
    , acceleration = "1000"
    , wait = "5.0"
    , start = "0.0"
    , increment = "0.5"
    , end = "calculate"
    , progress = Nothing
    }


type Msg
    = ToggleActive
    | ChangeName String
    | ChangePriority String
    | ChangeMode String
    | ChangeVelocity String
    | ChangeAcceleration String
    | ChangeStart String
    | ChangeIncrement String
    | ChangeEnd String
    | ChangeWait String
    | SendJson
    | UpdateProgress Json.Encode.Value
    | Close


port config : Json.Encode.Value -> Cmd msg


port processProgress : (Json.Encode.Value -> msg) -> Sub msg


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
            update SendJson { stage | priority = newValue }

        ChangeMode newValue ->
            update SendJson { stage | mode = newValue }

        ChangeVelocity newValue ->
            update SendJson { stage | velocity = newValue }

        ChangeAcceleration newValue ->
            update SendJson { stage | acceleration = newValue }

        ChangeStart newValue ->
            update SendJson { stage | start = newValue }

        ChangeIncrement newValue ->
            update SendJson { stage | increment = newValue, end = "calculate" }

        ChangeEnd newValue ->
            update SendJson { stage | increment = "calculate", end = newValue }

        ChangeWait newValue ->
            update SendJson { stage | wait = newValue }

        SendJson ->
            ( stage, config <| toJson stage )

        UpdateProgress progress ->
            ( { stage | progress = Just progress }, Cmd.none )

        Close ->
            let
                ( clearInstrument, sendJsonCmd ) =
                    update SendJson <| defaultModel
            in
                clearInstrument ! [ sendJsonCmd, removeModule "XPSControl" ]


main =
    Html.program
        { init = ( defaultModel, Cmd.none )
        , view = \stage -> Html.div [] (view stage)
        , update = update
        , subscriptions = \_ -> Sub.none
        }


view : Stage -> List (Html Msg)
view stage =
    ModuleHelpers.titleWithAttributions "XPS-controlled stages" stage.active ToggleActive Close attributions
        ++ if stage.active then
            nameView stage
                ++ [ ModuleHelpers.displayAllProgress stage.progress ]
           else
            [ Html.text "" ]


nameView : Stage -> List (Html Msg)
nameView stage =
    [ ModuleHelpers.dropDownBox "Name"
        stage.name
        ChangeName
        [ ( "None", "None" )
        , ( "ShortStage", "Short linear stage" )
        , ( "LongStage", "Long linear stage" )
        , ( "RotStage", "Rotational stage" )
        ]
    ]
        ++ (if stage.name == "None" then
                [ Html.text "" ]
            else
                [ ModuleHelpers.integerField "Priority" stage.priority ChangePriority
                , ModuleHelpers.dropDownBox "Mode"
                    stage.mode
                    ChangeMode
                    [ ( "incremental", "Incremental" )
                    , ( "continuous", "Continuous" )
                    ]
                ]
                    ++ (if stage.mode /= "RotStage" then
                            [ ModuleHelpers.floatField "Velocity" stage.velocity ChangeVelocity
                            , ModuleHelpers.floatField "Acceleration" stage.acceleration ChangeAcceleration
                            ]
                        else
                            [ Html.text "" ]
                       )
                    ++ [ ModuleHelpers.floatField "Wait time" stage.wait ChangeWait
                       , ModuleHelpers.floatField "Start" stage.start ChangeStart
                       ]
                    ++ (if stage.mode == "incremental" then
                            [ (if stage.increment == "calculate" then
                                ModuleHelpers.stringField "Increment" stage.increment ChangeIncrement
                               else
                                ModuleHelpers.floatField "Increment" stage.increment ChangeIncrement
                              )
                            , (if stage.end == "calculate" then
                                ModuleHelpers.stringField "End" stage.end ChangeEnd
                               else
                                ModuleHelpers.floatField "End" stage.end ChangeEnd
                              )
                            ]
                        else
                            [ Html.text "" ]
                       )
           )


toJson : Stage -> Json.Encode.Value
toJson stage =
    Json.Encode.list
        [ Json.Encode.object
            [ ( "python_module_name", Json.Encode.string "xps_control" )
            , ( "python_class_name", Json.Encode.string stage.name )
            , ( "elm_module_name", Json.Encode.string "XPSControl" )
            , ( "priority", Json.Encode.int (ModuleHelpers.intDefault defaultModel.priority stage.priority) )
            , ( "data_register"
              , Json.Encode.list
                    (List.map Json.Encode.string [ stage.name ++ "-position" ])
              )
            , ( "config"
              , Json.Encode.object
                    [ ( "mode", Json.Encode.string stage.mode )
                    , ( "velocity"
                      , Json.Encode.float
                            (ModuleHelpers.floatDefault defaultModel.velocity stage.velocity)
                      )
                    , ( "acceleration"
                      , Json.Encode.float
                            (ModuleHelpers.floatDefault defaultModel.acceleration stage.acceleration)
                      )
                    , ( "wait"
                      , Json.Encode.float
                            (ModuleHelpers.floatDefault defaultModel.wait stage.wait)
                      )
                    , ( "start"
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
