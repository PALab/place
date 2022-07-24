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
    , function_type : String
    , start_delay : String
    , func_duration : String
    , start_freq : String
    , stop_freq : String
    , sweep_duration : String
    , vary_amplitude : Bool
    , set_offset : Bool
    , start_amplitude : String
    , stop_amplitude : String
    , start_offset : String
    , stop_offset : String
    , wait_for_sweep : Bool
    , skip_last : Bool
    }


default : Model
default =
    { mode = "freq_sweep"
    , function_type = "sine"
    , start_delay = "0"
    , func_duration = "0"
    , start_freq = "1000"
    , stop_freq = "2000"
    , sweep_duration = "20"
    , vary_amplitude = False
    , set_offset = False
    , start_amplitude = "5"
    , stop_amplitude = "5"
    , start_offset = "0"
    , stop_offset = "0"
    , wait_for_sweep = True
    , skip_last = False
    }


type Msg
    = ToggleMode String
    | ToggleFuncType String
    | ChangeStartDelay String
    | ChangeFuncDuration String
    | ChangeStartFreq String
    | ChangeStopFreq String
    | ChangeSweepDuration String
    | ToggleAmplitude 
    | ToggleOffset 
    | ChangeStartAmplitude String
    | ChangeStopAmplitude String 
    | ChangeStartOffset String
    | ChangeStopOffset String
    | ToggleWait 
    | ToggleSkipLast


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        ToggleMode newMode ->
            ( { model | mode = newMode }, Cmd.none )

        ToggleFuncType newType ->
            ( { model | function_type = newType }, Cmd.none )    

        ChangeStartDelay newDelay ->
            ( { model | start_delay = newDelay }, Cmd.none )

        ChangeFuncDuration newTime ->
            ( { model | func_duration = newTime }, Cmd.none )

        ChangeStartFreq newStart ->
            ( { model | start_freq = newStart }, Cmd.none )

        ChangeStopFreq newStop ->
            ( { model | stop_freq = newStop }, Cmd.none )

        ChangeSweepDuration newDuration ->
            ( { model | sweep_duration = newDuration }, Cmd.none )

        ToggleAmplitude ->
            ( { model | vary_amplitude = not model.vary_amplitude }, Cmd.none )

        ToggleOffset ->
            ( { model | set_offset = not model.set_offset }, Cmd.none )            

        ChangeStartAmplitude newStartAmp ->
            ( { model | start_amplitude = newStartAmp }, Cmd.none )

        ChangeStopAmplitude newStopAmp ->
            ( { model | stop_amplitude = newStopAmp }, Cmd.none )

        ChangeStartOffset newStartOff ->
            ( { model | start_offset = newStartOff }, Cmd.none )

        ChangeStopOffset newStopOff ->
            ( { model | stop_offset = newStopOff }, Cmd.none )

        ToggleWait ->
            ( { model | wait_for_sweep = not model.wait_for_sweep }, Cmd.none )

        ToggleSkipLast ->
            ( { model | skip_last = not model.skip_last }, Cmd.none )


userInteractionsView : Model -> List (Html Msg)
userInteractionsView model =
    [ PluginHelpers.dropDownBox "Mode" model.mode ToggleMode [ ( "function", "Function" ) , ( "freq_sweep", "Frequency Sweep" )]
    ]
        ++ (if model.mode == "function" then
                [ PluginHelpers.dropDownBox "Function type" model.function_type ToggleFuncType [ ( "sine", "Sine" ) , ( "square", "Square" ) , ( "triangle", "Triangle" ) , ( "ramp", "Ramp" )]
                , PluginHelpers.floatField "Frequency (Hz)" model.start_freq ChangeStartFreq
                , PluginHelpers.floatField "Start delay (s)" model.start_delay ChangeStartDelay
                , PluginHelpers.floatField "Function duration (s, 0 for indefinite)" model.func_duration ChangeFuncDuration
                , PluginHelpers.checkbox "Vary amplitude" model.vary_amplitude ToggleAmplitude
                , PluginHelpers.checkbox "Set Offset" model.set_offset ToggleOffset
                ]
                    ++ (if not model.vary_amplitude then
                            [ PluginHelpers.floatField "Amplitude (Vpp)" model.start_amplitude ChangeStartAmplitude
                            ]
                                ++ (if model.set_offset then
                                        [ PluginHelpers.floatField "Offset (V)" model.start_offset ChangeStartOffset
                                        ] 
                                    else
                                        [ Html.text "" ]
                                    )
                        else
                            [ PluginHelpers.floatField "Start Amplitude (Vpp)" model.start_amplitude ChangeStartAmplitude
                            , PluginHelpers.floatField "Stop Amplitude (Vpp)" model.stop_amplitude ChangeStopAmplitude
                            ]
                                ++ (if model.set_offset then
                                        [ PluginHelpers.floatField "Start Offset (V)" model.start_offset ChangeStartOffset
                                        , PluginHelpers.floatField "Stop Offset (V)" model.stop_offset ChangeStopOffset
                                        ] 
                                    else
                                        [ Html.text "" ]
                                    )
                        )
                ++
                [ PluginHelpers.checkbox "Progress only when function is complete" model.wait_for_sweep ToggleWait
                , PluginHelpers.checkbox "Don't run on last update" model.skip_last ToggleSkipLast
                ]

            else
                (if model.mode == "freq_sweep" then
                    [ PluginHelpers.dropDownBox "Function type" model.function_type ToggleFuncType [ ( "sine", "Sine" ) , ( "square", "Square" ) , ( "triangle", "Triangle" ) , ( "ramp", "Ramp" )]
                    , PluginHelpers.floatField "Start frequency (Hz)" model.start_freq ChangeStartFreq
                    , PluginHelpers.floatField "Stop frequency (Hz)" model.stop_freq ChangeStopFreq
                    , PluginHelpers.floatField "Sweep duration (s)" model.sweep_duration ChangeSweepDuration
                    , PluginHelpers.checkbox "Vary amplitude" model.vary_amplitude ToggleAmplitude
                    , PluginHelpers.checkbox "Set Offset" model.set_offset ToggleOffset
                    ]
                        ++  (if not model.vary_amplitude then
                                [ PluginHelpers.floatField "Amplitude (Vpp)" model.start_amplitude ChangeStartAmplitude
                                ]
                                ++ (if model.set_offset then
                                        [ PluginHelpers.floatField "Offset (V)" model.start_offset ChangeStartOffset
                                        ] 
                                    else
                                        [ Html.text "" ]
                                    )
                            else
                                [ PluginHelpers.floatField "Start Amplitude (Vpp)" model.start_amplitude ChangeStartAmplitude
                                , PluginHelpers.floatField "Stop Amplitude (Vpp)" model.stop_amplitude ChangeStopAmplitude
                                ]
                                ++ (if model.set_offset then
                                        [ PluginHelpers.floatField "Start Offset (V)" model.start_offset ChangeStartOffset
                                        , PluginHelpers.floatField "Stop Offset (V)" model.stop_offset ChangeStopOffset
                                        ] 
                                    else
                                        [ Html.text "" ]
                                    )
                            )
                    ++
                    [ PluginHelpers.checkbox "Progress only when sweep is complete" model.wait_for_sweep ToggleWait
                    , PluginHelpers.checkbox "Don't run on last update" model.skip_last ToggleSkipLast
                    ]
                else
                    [ Html.text "" ]
                )
            )

encode : Model -> List ( String, E.Value )
encode model =
    [ ( "mode", E.string model.mode )
    , ( "function_type", E.string model.function_type )
    , ( "start_freq", E.float (PluginHelpers.floatDefault default.start_freq model.start_freq) )
    , ( "vary_amplitude", E.bool model.vary_amplitude )
    , ( "set_offset", E.bool model.set_offset )
    , ( "start_amplitude", E.float (PluginHelpers.floatDefault default.start_amplitude model.start_amplitude) )
    , ( "stop_amplitude", E.float (PluginHelpers.floatDefault default.stop_amplitude model.stop_amplitude) )
    , ( "start_offset", E.float (PluginHelpers.floatDefault default.start_offset model.start_offset) )
    , ( "stop_offset", E.float (PluginHelpers.floatDefault default.stop_offset model.stop_offset) )
    , ( "wait_for_sweep", E.bool model.wait_for_sweep )
    , ( "skip_last", E.bool model.skip_last )
    ]
        ++ (if model.mode == "function" then
                [ ( "start_delay", E.float (PluginHelpers.floatDefault default.start_delay model.start_delay) )
                , ( "func_duration", E.float (PluginHelpers.floatDefault default.func_duration model.func_duration) )
                ]

            else
                []
           )
        ++ (if model.mode == "freq_sweep" then
                [ ( "stop_freq", E.float (PluginHelpers.floatDefault default.stop_freq model.stop_freq) )
                , ( "sweep_duration", E.float (PluginHelpers.floatDefault default.sweep_duration model.sweep_duration) )
                ]

            else
                []
           )

decode : D.Decoder Model
decode =
    D.succeed
        Model
        |> required "mode" D.string
        |> required "function_type" D.string
        |> optional "start_delay" (D.float |> D.andThen (D.succeed << toString)) default.start_delay
        |> optional "func_duration" (D.float |> D.andThen (D.succeed << toString)) default.func_duration
        |> required "start_freq" (D.float |> D.andThen (D.succeed << toString))
        |> optional "stop_freq" (D.float |> D.andThen (D.succeed << toString)) default.stop_freq
        |> optional "sweep_duration" (D.float |> D.andThen (D.succeed << toString)) default.sweep_duration
        |> required "vary_amplitude" D.bool
        |> optional "set_offset" D.bool default.set_offset
        |> required "start_amplitude" (D.float |> D.andThen (D.succeed << toString))
        |> required "stop_amplitude" (D.float |> D.andThen (D.succeed << toString)) 
        |> required "start_offset" (D.float |> D.andThen (D.succeed << toString))
        |> required "stop_offset" (D.float |> D.andThen (D.succeed << toString)) 
        |> required "wait_for_sweep" D.bool
        |> required "skip_last" D.bool
        

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
