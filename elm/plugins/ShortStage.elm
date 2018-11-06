port module ShortStage exposing (main)

import Html exposing (Html)
import Json.Decode as D
import Json.Decode.Pipeline exposing (hardcoded, optional, required)
import Json.Encode as E
import Metadata exposing (Metadata)
import Plugin exposing (Plugin)
import PluginHelpers


common : Metadata
common =
    { title = "XPS-controlled short stage"
    , authors = [ "Paul Freeman" ]
    , maintainer = "Paul Freeman"
    , email = "paul.freeman.cs@gmail.com"
    , url = "https://github.com/palab/place"
    , elm =
        { moduleName = "ShortStage"
        }
    , python =
        { moduleName = "xps_control"
        , className = "ShortStage"
        }
    , defaultPriority = "20"
    }


type alias Model =
    { mode : String
    , velocity : String
    , acceleration : String
    , wait : String
    , start : String
    , increment : String
    , end : String
    }


default : Model
default =
    { mode = "incremental"
    , velocity = "50"
    , acceleration = "200"
    , wait = "5.0"
    , start = "0.0"
    , increment = "0.5"
    , end = "calculate"
    }


type Msg
    = ChangeMode String
    | ChangeVelocity String
    | ChangeAcceleration String
    | ChangeStart String
    | ChangeIncrement String
    | ChangeEnd String
    | ChangeWait String


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        ChangeMode newValue ->
            ( { model | mode = newValue }, Cmd.none )

        ChangeVelocity newValue ->
            ( { model | velocity = newValue }, Cmd.none )

        ChangeAcceleration newValue ->
            ( { model | acceleration = newValue }, Cmd.none )

        ChangeStart newValue ->
            ( { model | start = newValue }, Cmd.none )

        ChangeIncrement newValue ->
            ( { model | increment = newValue, end = "calculate" }, Cmd.none )

        ChangeEnd newValue ->
            ( { model | increment = "calculate", end = newValue }, Cmd.none )

        ChangeWait newValue ->
            ( { model | wait = newValue }, Cmd.none )


userInteractionsView : Model -> List (Html Msg)
userInteractionsView model =
    [ PluginHelpers.dropDownBox "Mode"
        model.mode
        ChangeMode
        [ ( "incremental", "Incremental" )
        , ( "continuous", "Continuous" )
        ]
    , PluginHelpers.floatField "Velocity" model.velocity ChangeVelocity
    , PluginHelpers.floatField "Acceleration" model.acceleration ChangeAcceleration
    , PluginHelpers.floatField "Wait time" model.wait ChangeWait
    , PluginHelpers.floatField "Start" model.start ChangeStart
    ]
        ++ (if model.mode == "incremental" then
                [ if model.increment == "calculate" then
                    PluginHelpers.stringField "Increment" model.increment ChangeIncrement

                  else
                    PluginHelpers.floatField "Increment" model.increment ChangeIncrement
                , if model.end == "calculate" then
                    PluginHelpers.stringField "End" model.end ChangeEnd

                  else
                    PluginHelpers.floatField "End" model.end ChangeEnd
                ]

            else
                [ Html.text "" ]
           )


encode : Model -> List ( String, E.Value )
encode model =
    [ ( "mode", E.string model.mode )
    , ( "velocity"
      , E.float
            (PluginHelpers.floatDefault default.velocity model.velocity)
      )
    , ( "acceleration"
      , E.float
            (PluginHelpers.floatDefault default.acceleration model.acceleration)
      )
    , ( "wait"
      , E.float
            (PluginHelpers.floatDefault default.wait model.wait)
      )
    , ( "start"
      , E.float
            (case String.toFloat model.start of
                Ok num ->
                    num

                otherwise ->
                    0.0
            )
      )
    , if model.end == "calculate" then
        ( "increment"
        , E.float
            (case String.toFloat model.increment of
                Ok num ->
                    num

                otherwise ->
                    1.0
            )
        )

      else
        ( "end"
        , E.float
            (case String.toFloat model.end of
                Ok num ->
                    num

                otherwise ->
                    1.0
            )
        )
    ]


decode : D.Decoder Model
decode =
    D.succeed Model
        |> required "mode" D.string
        |> required "velocity" (D.float |> D.andThen (D.succeed << toString))
        |> required "acceleration" (D.float |> D.andThen (D.succeed << toString))
        |> required "wait" (D.float |> D.andThen (D.succeed << toString))
        |> required "start" (D.float |> D.andThen (D.succeed << toString))
        |> optional "increment" (D.float |> D.andThen (D.succeed << toString)) "calculate"
        |> optional "end" (D.float |> D.andThen (D.succeed << toString)) "calculate"



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
