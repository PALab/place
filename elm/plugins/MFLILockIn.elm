port module MFLILockIn exposing (main)

import Html exposing (Html)
import Html.Attributes
import Html.Events
import Json.Decode as D
import Json.Decode.Pipeline exposing (optional, required)
import Json.Encode as E
import Metadata exposing (Metadata)
import Plugin exposing (Plugin)
import PluginHelpers exposing (anOption)


common : Metadata
common =
    { title = "MFLI Lock-In Amplifier"
    , authors = [ "Jonathan Simpson" ]
    , maintainer = "Jonathan Simpson"
    , email = "jsim921@aucklanduni.ac.nz"
    , url = "https://github.com/palab/place"
    , elm =
        { moduleName = "MFLILockIn"
        }
    , python =
        { moduleName = "mfli_lock_in"
        , className = "MFLILockIn"
        }
    , defaultPriority = "100"
    }

type alias Model =
    { mode : String
    , sigin_imp : String
    , sigin_range : String
    , ext_ref_channel : String
    , ext_ref_mode : String
    , demod_phaseshfit : String
    , demod_filter_en : Bool
    , timeconstant : String
    , sampling_rate : String
    , acquisition_time : String
    , trigger_source : String
    , trigger_type : String
    , trigger_level : String
    , trig_level_auto_range : Bool
    , plot : Bool
    }

default : Model
default =
    { mode = "lockin_amp"
    , sigin_imp = "imp_50"
    , sigin_range = "auto"
    , ext_ref_channel = "auxin_1"
    , ext_ref_mode = "auto"
    , demod_phaseshfit = "0.0"
    , demod_filter_en = False
    , timeconstant = "0.0001"
    , sampling_rate = "1000"
    , acquisition_time = "10"
    , trigger_source = "trigin_1"
    , trigger_type = "pos_edge"
    , trigger_level = "1.0"
    , trig_level_auto_range = True
    , plot = False
    }

type Msg
    = ChangeMode String
    | ChangeSiginImp String
    | ChangeSiginRange String
    | ChangeExtrefChannel String
    | ChangeExtrefMode String
    | ChangeDemodPhaseshift String
    | ToggleDemodFilter
    | ChangeTimeconstant String
    | ChangeSamplingRate String
    | ChangeAcquisitionTime String
    | ChangeTriggerSource String
    | ChangeTriggerType String
    | ChangeTriggerLevel String
    | ToggleTrigAutoRange
    | ChangePlot

update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        ChangeMode newMode ->
            ( { model | mode = newMode }, Cmd.none )

        ChangeSiginImp newImp ->
            ( { model | sigin_imp = newImp }, Cmd.none )

        ChangeSiginRange newRange ->
            ( { model | sigin_range = newRange }, Cmd.none )

        ChangeExtrefChannel newChannel ->
            ( { model | ext_ref_channel = newChannel }, Cmd.none )

        ChangeExtrefMode newMode ->
            ( { model | ext_ref_mode = newMode }, Cmd.none )

        ChangeDemodPhaseshift newPhase ->
            ( { model | demod_phaseshfit = newPhase }, Cmd.none )

        ToggleDemodFilter ->
            ( { model | demod_filter_en = not model.demod_filter_en }, Cmd.none )

        ChangeTimeconstant newConst ->
            ( { model | timeconstant = newConst }, Cmd.none )

        ChangeSamplingRate newRate ->
            ( { model | sampling_rate = newRate }, Cmd.none )

        ChangeAcquisitionTime newTime ->
            ( { model | acquisition_time = newTime }, Cmd.none )

        ChangeTriggerSource newSource ->
            ( { model | trigger_source = newSource }, Cmd.none )

        ChangeTriggerType newType ->
            ( { model | trigger_type = newType }, Cmd.none )

        ChangeTriggerLevel newLevel ->
            ( { model | trigger_level = newLevel }, Cmd.none )

        ToggleTrigAutoRange ->
            ( { model | trig_level_auto_range = not model.trig_level_auto_range }, Cmd.none )

        ChangePlot ->
            ( { model | plot = not model.plot }, Cmd.none )


userInteractionsView : Model -> List (Html Msg)
userInteractionsView model =
    [ PluginHelpers.dropDownBox "Instrument Mode" model.mode ChangeMode [("lockin_amp", "Lock-in Amplifier")]
    , Html.h4 [] [ Html.text "Signal Input" ]
    , PluginHelpers.dropDownBox "Input Impedance" model.sigin_imp ChangeSiginImp [("50_ohm", "50 Ω"), ("10_Mohm", "10 MΩ")]
    , PluginHelpers.dropDownBox "Input Range" model.sigin_range ChangeSiginRange [("auto", "Auto"), ("3_mv", "3 mV"), ("10_mv", "10 mV"), ("30_mv", "30 mV"), ("100_mv", "100 mV"), ("300_mv", "300 mV"), ("1_v", "1 V"), ("3_v", "3 V")]
    , Html.h4 [] [ Html.text "Reference" ]
    , PluginHelpers.dropDownBox "Reference Channel" model.ext_ref_channel ChangeExtrefChannel [("auxin_1", "Aux In 1"), ("auxin_2", "Aux In 2")]
    , PluginHelpers.dropDownBox "Reference Mode" model.ext_ref_mode ChangeExtrefMode [("auto", "Auto"), ("high_bw", "High Bandwidth"), ("low_bw", "Low Bandwidth")]
    , Html.h4 [] [ Html.text "Demodulator" ]
    , PluginHelpers.floatField "Demodulator Phase-shift" model.demod_phaseshfit ChangeDemodPhaseshift
    , PluginHelpers.checkbox "Filter Demodulated Signal" model.demod_filter_en ToggleDemodFilter 
    ]
        ++ (if model.demod_filter_en then
                    [ PluginHelpers.floatField "Filter Timeconstant (ms)" model.timeconstant ChangeTimeconstant
                    ]

                else
                    []
            )
    
            ++  [ Html.h4 [] [ Html.text "Acquisition" ]
                , PluginHelpers.floatField "Acquisition Time (s)" model.acquisition_time ChangeAcquisitionTime
                , PluginHelpers.floatField "Sampling Rate (Hz)" model.sampling_rate ChangeSamplingRate
                , PluginHelpers.dropDownBox "Trigger Source" model.trigger_source ChangeTriggerSource [("trigin_1", "Trig In 1"), ("trigin_2", "Trig In 2"), ("auxin_1", "Aux In 1"), ("auxin_2", "Aux In 2")]
                , PluginHelpers.dropDownBox "Trigger Type" model.trigger_type ChangeTriggerType [("pos_edge", "Positive Edge"), ("neg_edge", "Negative Edge")]
                , trigAutoRange model
                , PluginHelpers.checkbox "Plot" model.plot ChangePlot 
                ]

trigAutoRange : Model -> Html Msg
trigAutoRange model =
    Html.p [] <|
        [ Html.text "Trigger Level (V): "
        , Html.input
            [ Html.Attributes.value model.trigger_level
            , Html.Events.onInput ChangeTriggerLevel
            ]
            []
        , Html.text "    Auto Range:"
        , Html.input
            [ Html.Attributes.type_ "checkbox"
            , Html.Attributes.checked model.trig_level_auto_range
            , Html.Events.onClick ToggleTrigAutoRange
            ]
            []
        ]    
            ++ (case String.toFloat model.trigger_level of
                        Ok _ ->
                            []

                        Err error_msg ->
                            [ Html.br [] [], Html.span [ Html.Attributes.class "error-text" ] [ Html.text error_msg ] ]
                )

encode : Model -> List ( String, E.Value )
encode model =
    [ ( "mode", E.string model.mode )
    , ( "sigin_imp", E.string model.sigin_imp )
    , ( "sigin_range", E.string model.sigin_range )
    , ( "ext_ref_channel", E.string model.ext_ref_channel )
    , ( "ext_ref_mode", E.string model.ext_ref_mode )
    , ( "demod_phaseshfit", E.float (PluginHelpers.floatDefault default.demod_phaseshfit model.demod_phaseshfit) )
    , ( "demod_filter_en", E.bool model.demod_filter_en )
    , ( "timeconstant", E.float (PluginHelpers.floatDefault default.timeconstant model.timeconstant) )
    , ( "sampling_rate", E.float (PluginHelpers.floatDefault default.sampling_rate model.sampling_rate) )
    , ( "acquisition_time", E.float (PluginHelpers.floatDefault default.acquisition_time model.acquisition_time) )
    , ( "trigger_source", E.string model.trigger_source )
    , ( "trigger_type", E.string model.trigger_type )
    , ( "trigger_level", E.float (PluginHelpers.floatDefault default.trigger_level model.trigger_level) )
    , ( "trig_level_auto_range", E.bool model.trig_level_auto_range )
    , ( "plot", E.bool model.plot )
    ]

decode : D.Decoder Model
decode =
    D.succeed
        Model
        |> required "mode" D.string
        |> required "sigin_imp" D.string
        |> required "sigin_range" D.string
        |> required "ext_ref_channel" D.string
        |> required "ext_ref_mode" D.string
        |> required "demod_phaseshfit" (D.float |> D.andThen (D.succeed << toString))
        |> required "demod_filter_en" D.bool 
        |> required "timeconstant" (D.float |> D.andThen (D.succeed << toString)) 
        |> required "sampling_rate" (D.float |> D.andThen (D.succeed << toString))
        |> required "acquisition_time" (D.float |> D.andThen (D.succeed << toString))
        |> required "trigger_source" D.string
        |> required "trigger_type" D.string
        |> required "trigger_level" (D.float |> D.andThen (D.succeed << toString))
        |> required "trig_level_auto_range" D.bool
        |> required "plot" D.bool





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
