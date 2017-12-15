port module SR560PreAmp exposing (main)

import Html exposing (Html)
import Html.Events
import Html.Attributes
import Json.Encode
import ModuleHelpers


pythonModuleName =
    "sr560_preamp"


pythonClassName =
    "SR560PreAmp"


type alias Model =
    { className : String
    , active : Bool
    , priority : Int
    , blanking : String
    , coupling : String
    , reserve : String
    , mode : String
    , gain : String
    , highpass : String
    , lowpass : String
    , invert : String
    , source : String
    , vGainStat : String
    , vGain : Int
    }


defaultModel : Model
defaultModel =
    { className = "None"
    , active = False
    , priority = 10
    , blanking = "not blanked"
    , coupling = "DC"
    , reserve = "calibration gains"
    , mode = "bypass"
    , gain = "1"
    , highpass = "0.03 Hz"
    , lowpass = "1 MHz"
    , invert = "non-inverted"
    , source = "A"
    , vGainStat = "calibrated gain"
    , vGain = 20
    }


type Msg
    = ToggleActive
    | ChangePriority String
    | SendJson
    | Close
    | ChangeBlanking String
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


port jsonData : Json.Encode.Value -> Cmd msg


port removeModule : String -> Cmd msg


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
                    | priority = Result.withDefault 10 (String.toInt newPriority)
                }

        SendJson ->
            ( model
            , jsonData
                (Json.Encode.list
                    [ Json.Encode.object
                        [ ( "module_name", Json.Encode.string pythonModuleName )
                        , ( "class_name", Json.Encode.string model.className )
                        , ( "priority", Json.Encode.int model.priority )
                        , ( "data_register", Json.Encode.list (List.map Json.Encode.string []) )
                        , ( "config"
                          , Json.Encode.object
                                [ ( "blanking", Json.Encode.string model.blanking )
                                , ( "coupling", Json.Encode.string model.coupling )
                                , ( "reserve", Json.Encode.string model.reserve )
                                , ( "filter_mode", Json.Encode.string model.mode )
                                , ( "gain", Json.Encode.string model.gain )
                                , ( "highpass_filter", Json.Encode.string model.highpass )
                                , ( "lowpass_filter", Json.Encode.string model.lowpass )
                                , ( "signal_invert_sense", Json.Encode.string model.invert )
                                , ( "input_source", Json.Encode.string model.source )
                                , ( "vernier_gain_status", Json.Encode.string model.vGainStat )
                                , ( "vernier_gain", Json.Encode.int model.vGain )
                                ]
                          )
                        ]
                    ]
                )
            )

        Close ->
            let
                ( clearInstrument, sendJsonCmd ) =
                    updateModel SendJson <| defaultModel
            in
                clearInstrument ! [ sendJsonCmd, removeModule pythonModuleName ]

        ChangeBlanking newValue ->
            updateModel SendJson { model | blanking = newValue }

        ChangeCoupling newValue ->
            updateModel SendJson { model | coupling = newValue }

        ChangeReserve newValue ->
            updateModel SendJson { model | reserve = newValue }

        ChangeFilterMode newValue ->
            updateModel SendJson { model | mode = newValue }

        ChangeGain newValue ->
            updateModel SendJson { model | gain = newValue }

        ChangeHighpassFilter newValue ->
            updateModel SendJson { model | highpass = newValue }

        ChangeLowpassFilter newValue ->
            updateModel SendJson { model | lowpass = newValue }

        ChangeSignalInvertSense newValue ->
            updateModel SendJson { model | invert = newValue }

        ChangeInputSource newValue ->
            updateModel SendJson { model | source = newValue }

        ChangeVernierGainStatus newValue ->
            updateModel SendJson { model | vGainStat = newValue }

        ChangeVernierGain newValue ->
            updateModel SendJson
                { model
                    | vGain = Result.withDefault 20 (String.toInt newValue)
                }


main : Program Never Model Msg
main =
    Html.program
        { init = ( defaultModel, Cmd.none )
        , view = \model -> Html.div [] (viewModel model)
        , update = updateModel
        , subscriptions = \_ -> Sub.none
        }


viewModel : Model -> List (Html Msg)
viewModel model =
    ModuleHelpers.title "SRS SR560 Pre-Amp" model.active ToggleActive Close
        ++ if model.active then
            [ ModuleHelpers.integerField "Priority" model.priority ChangePriority
            , ModuleHelpers.dropDownBox "Amplifier Blanking"
                model.blanking
                ChangeBlanking
                [ ( "not blanked", "Not blanked" )
                , ( "blanked", "Blanked" )
                ]
            , ModuleHelpers.dropDownBox "Input coupling"
                model.coupling
                ChangeCoupling
                [ ( "ground", "Ground" )
                , ( "DC", "DC" )
                , ( "AC", "AC" )
                ]
            , ModuleHelpers.dropDownBox "Dynamic reserve"
                model.reserve
                ChangeReserve
                [ ( "low noise", "Low noise" )
                , ( "high DR", "High dynamic reserve" )
                , ( "calibration gains", "Calibration gains" )
                ]
            , ModuleHelpers.dropDownBox "Filter mode"
                model.mode
                ChangeFilterMode
                [ ( "bypass", "Bypass" )
                , ( "6 dB low pass", "6 dB low pass" )
                , ( "12 dB low pass", "12 dB low pass" )
                , ( "6 dB high pass", "6 dB high pass" )
                , ( "12 dB high pass", "12 dB high pass" )
                , ( "bandpass", "Bandpass" )
                ]
            , ModuleHelpers.dropDownBox "Gain"
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
            , ModuleHelpers.dropDownBox "Highpass filter"
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
            , ModuleHelpers.dropDownBox "Lowpass filter"
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
            , ModuleHelpers.dropDownBox "Signal invert sense"
                model.invert
                ChangeSignalInvertSense
                [ ( "non-inverted", "Non-inverted" )
                , ( "inverted", "Inverted" )
                ]
            , ModuleHelpers.dropDownBox "Input source"
                model.source
                ChangeInputSource
                [ ( "A", "Channel A" )
                , ( "B", "Channel B" )
                , ( "A-B", "A-B (differential)" )
                ]
            , ModuleHelpers.dropDownBox "Vernier gain status"
                model.vGainStat
                ChangeVernierGainStatus
                [ ( "calibrated gain", "Calibrated gain" )
                , ( "vernier gain", "Vernier gain" )
                ]
            , ModuleHelpers.integerField "Vernier gain (0-100%)" model.vGain ChangeVernierGain
            , ModuleHelpers.rangeCheck model.vGain 0 100 "Error: vernier gain is invalid"
            ]
           else
            [ ModuleHelpers.empty ]
