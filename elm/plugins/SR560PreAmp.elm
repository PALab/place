port module SR560PreAmp exposing (main)

import Html exposing (Html)
import Html.Attributes
import Json.Decode as D
import Json.Decode.Pipeline exposing (hardcoded, optional, required)
import Json.Encode as E
import Metadata exposing (Metadata)
import Plugin exposing (Plugin)
import PluginHelpers


common : Metadata
common =
    { title = "SRS SR560 Pre-Amp"
    , authors = [ "Paul Freeman" ]
    , maintainer = "Paul Freeman"
    , email = "paul.freeman.cs@gmail.com"
    , url = "https://github.com/palab/place"
    , elm =
        { moduleName = "SR560PreAmp"
        }
    , python =
        { moduleName = "sr560_preamp"
        , className = "SR560PreAmp"
        }
    , defaultPriority = "10"
    }


type alias Model =
    { blanking : String
    , coupling : String
    , reserve : String
    , mode : String
    , gain : String
    , highpass : String
    , lowpass : String
    , invert : String
    , source : String
    , vGainStat : String
    , vGain : String
    }


default : Model
default =
    { blanking = "not blanked"
    , coupling = "DC"
    , reserve = "calibration gains"
    , mode = "bypass"
    , gain = "1"
    , highpass = "0.03 Hz"
    , lowpass = "1 MHz"
    , invert = "non-inverted"
    , source = "A"
    , vGainStat = "calibrated gain"
    , vGain = "20"
    }


type Msg
    = ChangeBlanking String
    | ChangeCoupling String
    | ChangeReserve String
    | ChangeFilterMode String
    | ChangeGain String
    | ChangeHighpassFilter String
    | ChangeLowpassFilter String
    | ChangeSignalInvertSense String
    | ChangeInputSource String
    | ChangeVernierGainStatus String
    | ChangeVernierGain String


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        ChangeBlanking newValue ->
            ( { model | blanking = newValue }, Cmd.none )

        ChangeCoupling newValue ->
            ( { model | coupling = newValue }, Cmd.none )

        ChangeReserve newValue ->
            ( { model | reserve = newValue }, Cmd.none )

        ChangeFilterMode newValue ->
            ( { model | mode = newValue }, Cmd.none )

        ChangeGain newValue ->
            ( { model | gain = newValue }, Cmd.none )

        ChangeHighpassFilter newValue ->
            ( { model | highpass = newValue }, Cmd.none )

        ChangeLowpassFilter newValue ->
            ( { model | lowpass = newValue }, Cmd.none )

        ChangeSignalInvertSense newValue ->
            ( { model | invert = newValue }, Cmd.none )

        ChangeInputSource newValue ->
            ( { model | source = newValue }, Cmd.none )

        ChangeVernierGainStatus newValue ->
            ( { model | vGainStat = newValue }, Cmd.none )

        ChangeVernierGain newValue ->
            ( { model | vGain = newValue }, Cmd.none )


userInteractionsView : Model -> List (Html Msg)
userInteractionsView model =
    [ Html.div [ Html.Attributes.style [("margin-top", "15px"), ("margin-bottom", "15px")] ] [ Html.text "Warning: The SR560 preamplifier is a listen-only instrument and cannot send information back to PLACE via serial. Please ensure you positively verify that the correct serial port is provided for this instrument in the PLACE configuration file (PLACE Configuration tab)." ]
    , Html.br [] []    
    , PluginHelpers.dropDownBox "Amplifier Blanking"
        model.blanking
        ChangeBlanking
        [ ( "not blanked", "Not blanked" )
        , ( "blanked", "Blanked" )
        ]
    , PluginHelpers.dropDownBox "Input coupling"
        model.coupling
        ChangeCoupling
        [ ( "ground", "Ground" )
        , ( "DC", "DC" )
        , ( "AC", "AC" )
        ]
    , PluginHelpers.dropDownBox "Dynamic reserve"
        model.reserve
        ChangeReserve
        [ ( "low noise", "Low noise" )
        , ( "high DR", "High dynamic reserve" )
        , ( "calibration gains", "Calibration gains" )
        ]
    , PluginHelpers.dropDownBox "Filter mode"
        model.mode
        ChangeFilterMode
        [ ( "bypass", "Bypass" )
        , ( "6 dB low pass", "6 dB low pass" )
        , ( "12 dB low pass", "12 dB low pass" )
        , ( "6 dB high pass", "6 dB high pass" )
        , ( "12 dB high pass", "12 dB high pass" )
        , ( "bandpass", "Bandpass" )
        ]
    , PluginHelpers.dropDownBox "Gain"
        model.gain
        ChangeGain
        [ ( "1", "1" )
        , ( "2", "2" )
        , ( "5", "5" )
        , ( "10", "10" )
        , ( "20", "20" )
        , ( "50", "50" )
        , ( "100", "100" )
        , ( "200", "200" )
        , ( "500", "500" )
        , ( "1 k", "1 k" )
        , ( "2 k", "2 k" )
        , ( "5 k", "5 k" )
        , ( "10 k", "10 k" )
        , ( "20 k", "20 k" )
        , ( "50 k", "50 k" )
        ]
    , PluginHelpers.dropDownBox "Highpass filter"
        model.highpass
        ChangeHighpassFilter
        [ ( "0.03 Hz", "0.03 Hz" )
        , ( "0.1 Hz", "0.1 Hz" )
        , ( "0.3 Hz", "0.3 Hz" )
        , ( "1 Hz", "1 Hz" )
        , ( "3 Hz", "3 Hz" )
        , ( "10 Hz", "10 Hz" )
        , ( "30 Hz", "30 Hz" )
        , ( "100 Hz", "100 Hz" )
        , ( "300 Hz", "300 Hz" )
        , ( "1 kHz", "1 kHz" )
        , ( "3 kHz", "3 kHz" )
        , ( "10 kHz", "10 kHz" )
        ]
    , PluginHelpers.dropDownBox "Lowpass filter"
        model.lowpass
        ChangeLowpassFilter
        [ ( "0.03 Hz", "0.03 Hz" )
        , ( "0.1 Hz", "0.1 Hz" )
        , ( "0.3 Hz", "0.3 Hz" )
        , ( "1 Hz", "1 Hz" )
        , ( "3 Hz", "3 Hz" )
        , ( "10 Hz", "10 Hz" )
        , ( "30 Hz", "30 Hz" )
        , ( "100 Hz", "100 Hz" )
        , ( "300 Hz", "300 Hz" )
        , ( "1 kHz", "1 kHz" )
        , ( "3 kHz", "3 kHz" )
        , ( "10 kHz", "10 kHz" )
        , ( "30 kHz", "30 kHz" )
        , ( "100 kHz", "100 kHz" )
        , ( "300 kHz", "300 kHz" )
        , ( "1 MHz", "1 MHz" )
        ]
    , PluginHelpers.dropDownBox "Signal invert sense"
        model.invert
        ChangeSignalInvertSense
        [ ( "non-inverted", "Non-inverted" )
        , ( "inverted", "Inverted" )
        ]
    , PluginHelpers.dropDownBox "Input source"
        model.source
        ChangeInputSource
        [ ( "A", "Channel A" )
        , ( "B", "Channel B" )
        , ( "A-B", "A-B (differential)" )
        ]
    , PluginHelpers.dropDownBox "Vernier gain status"
        model.vGainStat
        ChangeVernierGainStatus
        [ ( "calibrated gain", "Calibrated gain" )
        , ( "vernier gain", "Vernier gain" )
        ]
    , PluginHelpers.integerField "Vernier gain (0-100%)" model.vGain ChangeVernierGain
    , PluginHelpers.rangeCheck model.vGain 0 100 "Error: vernier gain is invalid"
    ]


encode : Model -> List ( String, E.Value )
encode model =
    [ ( "blanking", E.string model.blanking )
    , ( "coupling", E.string model.coupling )
    , ( "reserve", E.string model.reserve )
    , ( "filter_mode", E.string model.mode )
    , ( "gain", E.string model.gain )
    , ( "highpass_filter", E.string model.highpass )
    , ( "lowpass_filter", E.string model.lowpass )
    , ( "signal_invert_sense", E.string model.invert )
    , ( "input_source", E.string model.source )
    , ( "vernier_gain_status", E.string model.vGainStat )
    , ( "vernier_gain", E.int (PluginHelpers.intDefault default.vGain model.vGain) )
    ]


decode : D.Decoder Model
decode =
    D.succeed
        Model
        |> required "blanking" D.string
        |> required "coupling" D.string
        |> required "reserve" D.string
        |> required "filter_mode" D.string
        |> required "gain" D.string
        |> required "highpass_filter" D.string
        |> required "lowpass_filter" D.string
        |> required "signal_invert_sense" D.string
        |> required "input_source" D.string
        |> required "vernier_gain_status" D.string
        |> required "vernier_gain" (D.int |> D.andThen (D.succeed << toString))



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
