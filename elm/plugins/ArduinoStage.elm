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
    }


type Msg
    = ToggleActive
    | ChangePriority String
    | ChangeStart String
    | ChangeInc String
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
    }


viewModel : Model -> List (Html Msg)
viewModel model =
    ModuleHelpers.title "Arduino-controlled Stage" model.active ToggleActive Close
        ++ if model.active then
            [ ModuleHelpers.integerField "Priority" model.priority ChangePriority
            , ModuleHelpers.floatField "Start" model.start ChangeStart
            , ModuleHelpers.floatField "Increment" model.increment ChangeInc
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
            updateModel SendJson { model | increment = newInc }

        SendJson ->
            ( model
            , jsonData
                (Json.Encode.list
                    [ Json.Encode.object
                        [ ( "module_name", Json.Encode.string pythonModuleName )
                        , ( "class_name", Json.Encode.string model.className )
                        , ( "priority", Json.Encode.int (ModuleHelpers.intDefault defaultModel.priority model.priority) )
                        , ( "data_register", Json.Encode.list (List.map Json.Encode.string []) )
                        , ( "config"
                          , Json.Encode.object
                                [ ( "start", Json.Encode.float (ModuleHelpers.floatDefault defaultModel.start model.start) )
                                , ( "increment", Json.Encode.float (ModuleHelpers.floatDefault defaultModel.increment model.increment) )
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
                clearModel ! [ clearModelCmd, removeModule pythonModuleName ]
