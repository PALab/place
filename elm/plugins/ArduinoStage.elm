port module ArduinoStage exposing (main)

import Html exposing (Html)
import Json.Decode as D
import Json.Decode.Pipeline exposing (required, optional)
import Json.Encode as E
import Metadata exposing (Metadata)
import Plugin exposing (Plugin)
import PluginHelpers

common : Metadata
common =
    { title = "Arduino Rotational Stage" 
    , authors = [ "Jonathan Simpson" ] 
    , maintainer = "Jonathan Simpson"
    , email = "jim921@aucklanduni.ac.nz"
    , url = "https://github.com/palab/place"
    , elm =
        { moduleName = "ArduinoStage" 
        }
    , python =
        { moduleName = "arduino_stage" 
        , className = "ArduinoStage"
        }
    , defaultPriority = "5"}


type alias Model =
    { start : String
    , increment : String
    , end : String
    , wait : String
    }


default : Model
default =
    {   start = "0.0" 
      , increment = "1.8"
      , end = "calculate"
      , wait = "1.0"
    }



type Msg
    =  ChangeStart String
    |  ChangeInc String
    |  ChangeEnd String
    |  ChangeWait String



update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        ChangeStart newStart ->
            ( { model | start = newStart }, Cmd.none)

        ChangeInc newInc ->
                ( { model | increment = newInc, end = "calculate"}, Cmd.none)

        ChangeEnd newEnd ->
                ( { model | increment = "calculate", end = newEnd}, Cmd.none )

        ChangeWait newWait ->
                ( { model | wait = newWait}, Cmd.none )


userInteractionsView : Model -> List (Html Msg)
userInteractionsView model =
            [ PluginHelpers.floatField "Start" model.start ChangeStart
            , PluginHelpers.floatStringField "Increment" model.increment "calculate" ChangeInc
            , PluginHelpers.floatStringField "End" model.end "calculate" ChangeEnd
            , PluginHelpers.floatField "Wait Time" model.wait ChangeWait
            ]


encode : Model -> List ( String, E.Value )
encode model =
    [ (  "start" , E.float (PluginHelpers.floatDefault default.start model.start) ) 
        , if model.end == "calculate" then
              ( "increment", E.float (PluginHelpers.floatDefault default.increment model.increment) ) 
          else
              ( "end", E.float (PluginHelpers.floatDefault default.end model.end) ) 
        , ( "wait", E.float (PluginHelpers.floatDefault default.wait model.wait) ) 
    ]


decode : D.Decoder Model
decode =
    D.succeed
        Model
        |> required "start" (D.float |> D.andThen (D.succeed << toString))
        |> optional "increment" (D.float |> D.andThen (D.succeed << toString)) "calculate"
        |> optional "end" (D.float |> D.andThen (D.succeed << toString)) "calculate"
        |> required "wait" (D.float |> D.andThen (D.succeed << toString)) 



-- THE END
-- What follows this is some additional code to handle some of the information
-- you provided above. Beginning users won't need to change it, but PLACE is
-- certainly capable of a great many features when harnessed by an advanced
-- user.
--
--
----------------------------------------------
-- THINGS YOU PROBABLY DON"T NEED TO CHANGE --
----------------------------------------------


port config : E.Value -> Cmd msg


port removePlugin : String -> Cmd msg


port processProgress : (E.Value -> msg) -> Sub msg


main : Program Never PluginModel PluginMsg
main =
    Html.program
        { init = ( defaultModel, Cmd.none )
        , view = \model -> Html.div [] (viewModel model)
        , update = updatePlugin
        , subscriptions = always <| processProgress UpdateProgress
        }


type alias PluginModel =
    { active : Bool
    , priority : String
    , metadata : Metadata
    , config : Model
    , progress : E.Value
    }


defaultModel : PluginModel
defaultModel =
    { active = False
    , priority = common.defaultPriority
    , metadata = common
    , config = default
    , progress = E.null
    }


type PluginMsg
    = ToggleActive ------------ turn the plugin on and off on the webpage
    | ChangePriority String --- change the order of execution, relative to other plugins
    | ChangePlugin Msg -------- change one of the custom values in the plugin
    | SendToPlace ------------- sends the values in the model to PLACE
    | UpdateProgress E.Value -- update current progress of a running experiment
    | Close ------------------- close the plugin tab on the webpage


newModel : PluginModel -> ( PluginModel, Cmd PluginMsg )
newModel model =
    updatePlugin SendToPlace model


viewModel : PluginModel -> List (Html PluginMsg)
viewModel model =
    PluginHelpers.titleWithAttributions
        common.title
        model.active
        ToggleActive
        Close
        common.authors
        common.maintainer
        common.email
        ++ (if model.active then
                PluginHelpers.integerField "Priority" model.priority ChangePriority
                    :: List.map (Html.map ChangePlugin) (userInteractionsView model.config)
                    ++ [ PluginHelpers.displayAllProgress model.progress ]

            else
                [ Html.text "" ]
           )


updatePlugin : PluginMsg -> PluginModel -> ( PluginModel, Cmd PluginMsg )
updatePlugin msg model =
    case msg of
        ToggleActive ->
            if model.active then
                newModel { model | active = False }

            else
                newModel { model | active = True }

        ChangePriority newPriority ->
            newModel { model | priority = newPriority }

        ChangePlugin pluginMsg ->
            let
                config =
                    model.config

                ( newConfig, cmd ) =
                    update pluginMsg model.config

                newCmd =
                    Cmd.map ChangePlugin cmd

                ( updatedModel, updatedCmd ) =
                    newModel { model | config = newConfig }
            in
            ( updatedModel, Cmd.batch [ newCmd, updatedCmd ] )

        SendToPlace ->
            ( model
            , config <|
                E.object
                    [ ( model.metadata.elm.moduleName
                      , Plugin.encode
                            { active = model.active
                            , priority = PluginHelpers.intDefault model.metadata.defaultPriority model.priority
                            , metadata = model.metadata
                            , config = E.object (encode model.config)
                            , progress = E.null
                            }
                      )
                    ]
            )

        UpdateProgress value ->
            case D.decodeValue Plugin.decode value of
                Err err ->
                    ( { model | progress = E.string <| "Decode plugin error: " ++ err }, Cmd.none )

                Ok plugin ->
                    if plugin.active then
                        case D.decodeValue decode plugin.config of
                            Err err ->
                                ( { model | progress = E.string <| "Decode value error: " ++ err }, Cmd.none )

                            Ok config ->
                                newModel
                                    { active = plugin.active
                                    , priority = toString plugin.priority
                                    , metadata = plugin.metadata
                                    , config = config
                                    , progress = plugin.progress
                                    }

                    else
                        newModel defaultModel

        Close ->
            let
                ( clearModel, clearModelCmd ) =
                    newModel defaultModel
            in
            ( clearModel, Cmd.batch [ clearModelCmd, removePlugin model.metadata.elm.moduleName ] )
