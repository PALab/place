port module DS345 exposing (main)

import Html exposing (Html)
import Json.Decode as D
import Json.Decode.Pipeline exposing (hardcoded, optional, required)
import Json.Encode as E
import Metadata exposing (Metadata)
import Plugin exposing (Plugin)
import PluginHelpers


common : Metadata
common =
    { title = "DS345 Function Generator"
    , authors = [ "Paul Freeman", "Jonathan Simpson" ]
    , maintainer = "Jonathan Simpson"
    , email = "jsim921@aucklanduni.ac.nz"
    , url = "https://github.com/palab/place"
    , elm =
        { moduleName = "DS345"
        }
    , python =
        { moduleName = "ds345_function_gen"
        , className = "DS345"
        }
    , defaultPriority = "15"
    }


type alias Model =
    { mode : String
    , start_freq : String
    , stop_freq : String
    , sweep_duration : String
    , vary_amplitude : Bool
    , start_amplitude : String
    , stop_amplitude : String
    , wait_for_sweep : Bool
    }


default : Model
default =
    { mode = "freq_sweep"
    , start_freq = "1000"
    , stop_freq = "2000"
    , sweep_duration = "20"
    , vary_amplitude = False
    , start_amplitude = "5"
    , stop_amplitude = "5"
    , wait_for_sweep = True
    }


type Msg
    = ToggleMode String
    | ChangeStartFreq String
    | ChangeStopFreq String
    | ChangeSweepDuration String
    | ToggleAmplitude 
    | ChangeStartAmplitude String
    | ChangeStopAmplitude String
    | ToggleWait 


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        ToggleMode newMode ->
            ( { model | mode = newMode }, Cmd.none )

        ChangeStartFreq newStart ->
            ( { model | start_freq = newStart }, Cmd.none )

        ChangeStopFreq newStop ->
            ( { model | stop_freq = newStop }, Cmd.none )

        ChangeSweepDuration newDuration ->
            ( { model | sweep_duration = newDuration }, Cmd.none )

        ToggleAmplitude ->
            ( { model | vary_amplitude = not model.vary_amplitude, stop_amplitude = model.start_amplitude }, Cmd.none )

        ChangeStartAmplitude newStartAmp ->
            ( { model | start_amplitude = newStartAmp }, Cmd.none )

        ChangeStopAmplitude newStopAmp ->
            ( { model | stop_amplitude = newStopAmp }, Cmd.none )

        ToggleWait ->
            ( { model | wait_for_sweep = not model.wait_for_sweep }, Cmd.none )


userInteractionsView : Model -> List (Html Msg)
userInteractionsView model =
    [ PluginHelpers.dropDownBox "Mode" model.mode ToggleMode [ ( "freq_sweep", "Frequency Sweep" )]
    ]
        ++ (if model.mode == "freq_sweep" then
                [ PluginHelpers.floatField "Start frequency (Hz)" model.start_freq ChangeStartFreq
                , PluginHelpers.floatField "Stop frequency (Hz)" model.stop_freq ChangeStopFreq
                , PluginHelpers.floatField "Sweep duration (s)" model.sweep_duration ChangeSweepDuration
                , PluginHelpers.checkbox "Vary amplitude" model.vary_amplitude ToggleAmplitude
                ]
                    ++ (if not model.vary_amplitude then
                            [ PluginHelpers.floatField "Amplitude (Vpp)" model.start_amplitude ChangeStartAmplitude
                            ]

                        else
                            [ PluginHelpers.floatField "Start Amplitude (Vpp)" model.start_amplitude ChangeStartAmplitude
                            , PluginHelpers.floatField "Stop Amplitude (Vpp)" model.stop_amplitude ChangeStopAmplitude
                            ]
                        )
                ++
                [ PluginHelpers.checkbox "Progress only when sweep is complete" model.wait_for_sweep ToggleWait
                ]

            else
                [ Html.text "" ]
           )

encode : Model -> List ( String, E.Value )
encode model =
    [ ( "mode", E.string model.mode )
    , ( "start_freq", E.float (PluginHelpers.floatDefault default.start_freq model.start_freq) )
    , ( "stop_freq", E.float (PluginHelpers.floatDefault default.stop_freq model.stop_freq) )
    , ( "sweep_duration", E.float (PluginHelpers.floatDefault default.sweep_duration model.sweep_duration) )
    , ( "vary_amplitude", E.bool model.vary_amplitude )
    , ( "start_amplitude", E.float (PluginHelpers.floatDefault default.start_amplitude model.start_amplitude) )
    , ( "stop_amplitude", E.float (PluginHelpers.floatDefault default.stop_amplitude model.stop_amplitude) )
    , ( "wait_for_sweep", E.bool model.wait_for_sweep )
    ]


decode : D.Decoder Model
decode =
    D.succeed
        Model
        |> required "mode" D.string
        |> required "start_freq" (D.float |> D.andThen (D.succeed << toString))
        |> required "stop_freq" (D.float |> D.andThen (D.succeed << toString))
        |> required "sweep_duration" (D.float |> D.andThen (D.succeed << toString))
        |> required "vary_amplitude" D.bool
        |> required "start_amplitude" (D.float |> D.andThen (D.succeed << toString))
        |> required "stop_amplitude" (D.float |> D.andThen (D.succeed << toString))
        |> required "wait_for_sweep" D.bool



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
                            , metadata = common
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
                                    , metadata = common
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
