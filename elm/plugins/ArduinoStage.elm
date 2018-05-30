port module ArduinoStage exposing (main)

import Html exposing (Html)
import Html.Events
import Html.Attributes
import Json.Encode
import ModuleHelpers


pythonModuleName =
    "arduino_stage"


pythonClassName =
    "ArduinoStage"


type alias Model =
    { className : String
    , active : Bool
    , priority : String
    , start : String
    , increment : String
    , end : String
    , wait : String
    }


type Msg
    = ToggleActive
    | ChangePriority String
    | ChangeStart String
    | ChangeInc String
    | ChangeEnd String
    | ChangeWait String
    | SendJson
    | Close


port jsonData : Json.Encode.Value -> Cmd msg


port removeModule : String -> Cmd msg


main : Program Never Model Msg
main =
    Html.program
        { init = ( defaultModel, Cmd.none )
        , view = \model -> Html.div [] (viewModel model)
        , update = updateModel
        , subscriptions = \_ -> Sub.none
        }


defaultModel : Model
defaultModel =
    { className = "None"
    , active = False
    , priority = "10"
    , start = "0.0"
    , increment = "1.0"
    , end = "calculate"
    , wait = "2.0"
    }


viewModel : Model -> List (Html Msg)
viewModel model =
    ModuleHelpers.title "Arduino-controlled Stage" model.active ToggleActive Close
        ++ if model.active then
            [ ModuleHelpers.integerField "Priority" model.priority ChangePriority
            , ModuleHelpers.floatField "Start" model.start ChangeStart
            , ModuleHelpers.floatStringField "Increment" model.increment "calculate" ChangeInc
            , ModuleHelpers.floatStringField "End" model.end "calculate" ChangeEnd
            , ModuleHelpers.floatField "Wait Time" model.wait ChangeWait
            ]
           else
            [ ModuleHelpers.empty ]


updateModel : Msg -> Model -> ( Model, Cmd Msg )
updateModel msg model =
    case msg of
        ToggleActive ->
            if model.active then
                updateModel SendJson
                    { model
                        | className = "None"
                        , active = False
                    }
            else
                updateModel SendJson
                    { model
                        | className = pythonClassName
                        , active = True
                    }

        ChangePriority newPriority ->
            updateModel SendJson { model | priority = newPriority }

        ChangeStart newStart ->
            updateModel SendJson { model | start = newStart }

        ChangeInc newInc ->
            updateModel SendJson
                { model
                    | increment = newInc
                    , end = "calculate"
                }

        ChangeEnd newEnd ->
            updateModel SendJson
                { model
                    | increment = "calculate"
                    , end = newEnd
                }

        ChangeWait newWait ->
            updateModel SendJson
                { model
                    | wait = newWait
                }

        SendJson ->
            ( model
            , jsonData
                (Json.Encode.list
                    [ Json.Encode.object
                        [ ( "module_name", Json.Encode.string pythonModuleName )
                        , ( "class_name", Json.Encode.string model.className )
                        , ( "priority", Json.Encode.int (ModuleHelpers.intDefault defaultModel.priority model.priority) )
                        , ( "data_register", Json.Encode.list (List.map Json.Encode.string [ model.className ++ "-position" ]) )
                        , ( "config"
                          , Json.Encode.object
                                [ ( "start"
                                  , Json.Encode.float
                                        (Result.withDefault 0.0
                                            (String.toFloat model.start)
                                        )
                                  )
                                , if model.end == "calculate" then
                                    ( "increment"
                                    , Json.Encode.float
                                        (Result.withDefault 1.0
                                            (String.toFloat model.increment)
                                        )
                                    )
                                  else
                                    ( "end"
                                    , Json.Encode.float
                                        (Result.withDefault 0.0
                                            (String.toFloat model.end)
                                        )
                                    )
                                , ( "wait"
                                  , Json.Encode.float
                                        (Result.withDefault 2.0
                                            (String.toFloat model.wait)
                                        )
                                  )
                                ]
                          )
                        ]
                    ]
                )
            )

        Close ->
            let
                ( clearModel, clearModelCmd ) =
                    updateModel SendJson <| defaultModel
            in
                clearModel ! [ clearModelCmd, removeModule pythonClassName ]
