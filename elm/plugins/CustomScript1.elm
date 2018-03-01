port module CustomScript1 exposing (main)

import Html exposing (Html)
import Html.Events
import Html.Attributes
import Json.Encode
import ModuleHelpers


placeModuleTitle =
    "Custom Script #1"


pythonModuleName =
    "custom_script_1"


pythonClassName =
    "CustomScript1"


type alias Model =
    { moduleName : String
    , className : String
    , active : Bool
    , priority : Int
    , scriptPath : String
    }


type Msg
    = ToggleActive
    | ChangePriority String
    | ChangeScriptPath String
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
    { moduleName = pythonModuleName
    , className = "None"
    , active = False
    , priority = 999
    , scriptPath = ""
    }


viewModel : Model -> List (Html Msg)
viewModel model =
    ModuleHelpers.title placeModuleTitle model.active ToggleActive Close
        ++ if model.active then
            [ ModuleHelpers.integerField "Priority" model.priority ChangePriority
            , ModuleHelpers.stringField "Script path" model.scriptPath ChangeScriptPath
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
            updateModel SendJson
                { model
                    | priority = Result.withDefault 999 (String.toInt newPriority)
                }

        ChangeScriptPath newPath ->
            updateModel SendJson
                { model | scriptPath = newPath }

        SendJson ->
            ( model
            , jsonData
                (Json.Encode.list
                    [ Json.Encode.object
                        [ ( "module_name", Json.Encode.string model.moduleName )
                        , ( "class_name", Json.Encode.string model.className )
                        , ( "priority", Json.Encode.int model.priority )
                        , ( "data_register"
                          , Json.Encode.list
                                (List.map Json.Encode.string
                                    [ "CustomScript1-exit_code" ]
                                )
                          )
                        , ( "config"
                          , Json.Encode.object
                                [ ( "script_path", Json.Encode.string model.scriptPath )
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
