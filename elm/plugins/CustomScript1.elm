port module CustomScript1 exposing (main)

import Html exposing (Html)
import Html.Events
import Html.Attributes
import Json.Encode
import ModuleHelpers


attributions : ModuleHelpers.Attributions
attributions =
    { authors = [ "Paul Freeman" ]
    , maintainer = "Paul Freeman"
    , maintainerEmail = "pfre484@aucklanduni.ac.nz"
    }


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
    , priority : String
    , configScriptPath : String
    , updateScriptPath : String
    , cleanupScriptPath : String
    , progress : Maybe Json.Encode.Value
    }


type Msg
    = ToggleActive
    | ChangePriority String
    | ChangeConfigScriptPath String
    | ChangeUpdateScriptPath String
    | ChangeCleanupScriptPath String
    | SendJson
    | UpdateProgress Json.Encode.Value
    | Close


port config : Json.Encode.Value -> Cmd msg


port processProgress : (Json.Encode.Value -> msg) -> Sub msg


port removeModule : String -> Cmd msg


main : Program Never Model Msg
main =
    Html.program
        { init = ( defaultModel, Cmd.none )
        , view = \model -> Html.div [] (viewModel model)
        , update = updateModel
        , subscriptions = always <| processProgress UpdateProgress
        }


defaultModel : Model
defaultModel =
    { moduleName = pythonModuleName
    , className = "None"
    , active = False
    , priority = "999"
    , configScriptPath = ""
    , updateScriptPath = ""
    , cleanupScriptPath = ""
    , progress = Nothing
    }


viewModel : Model -> List (Html Msg)
viewModel model =
    ModuleHelpers.titleWithAttributions placeModuleTitle model.active ToggleActive Close attributions
        ++ if model.active then
            [ ModuleHelpers.integerField "Priority" model.priority ChangePriority
            , ModuleHelpers.stringField "Config script path" model.configScriptPath ChangeConfigScriptPath
            , ModuleHelpers.stringField "Update script path" model.updateScriptPath ChangeUpdateScriptPath
            , ModuleHelpers.stringField "Cleanup script path" model.cleanupScriptPath ChangeCleanupScriptPath
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

        ChangeConfigScriptPath newPath ->
            updateModel SendJson { model | configScriptPath = newPath }

        ChangeUpdateScriptPath newPath ->
            updateModel SendJson { model | updateScriptPath = newPath }

        ChangeCleanupScriptPath newPath ->
            updateModel SendJson { model | cleanupScriptPath = newPath }

        SendJson ->
            ( model
            , config
                (Json.Encode.list
                    [ Json.Encode.object
                        [ ( "python_module_name", Json.Encode.string model.moduleName )
                        , ( "python_class_name", Json.Encode.string model.className )
                        , ( "elm_module_name", Json.Encode.string "CustomScript1" )
                        , ( "priority"
                          , Json.Encode.int
                                (ModuleHelpers.intDefault defaultModel.priority model.priority)
                          )
                        , ( "data_register"
                          , Json.Encode.list
                                (List.map Json.Encode.string
                                    [ "CustomScript1-exit_code" ]
                                )
                          )
                        , ( "config"
                          , Json.Encode.object
                                [ ( "config_script_path", Json.Encode.string model.configScriptPath )
                                , ( "update_script_path", Json.Encode.string model.updateScriptPath )
                                , ( "cleanup_script_path", Json.Encode.string model.cleanupScriptPath )
                                ]
                          )
                        ]
                    ]
                )
            )

        UpdateProgress progress ->
            ( { model | progress = Just progress }, Cmd.none )

        Close ->
            let
                ( clearModel, clearModelCmd ) =
                    updateModel SendJson <| defaultModel
            in
                clearModel ! [ clearModelCmd, removeModule pythonClassName ]
