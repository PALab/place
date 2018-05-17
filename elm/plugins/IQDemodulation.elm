port module IQDemodulation exposing (main)

import Html exposing (Html)
import Html.Events
import Html.Attributes
import Json.Encode
import ModuleHelpers exposing (..)


attributions : ModuleHelpers.Attributions
attributions =
    { authors = [ "Sam Hitchman", "Paul Freeman" ]
    , maintainer = "Sam Hitchman"
    , maintainerEmail = "shit014@aucklanduni.ac.nz"
    }


type alias Model =
    { moduleName : String
    , className : String
    , active : Bool
    , priority : String
    , plot : Bool
    , fieldEnding : String
    , removeData : Bool
    , lowpassCutoff : String
    , yShift : String
    }


type Msg
    = ToggleActive
    | TogglePlot
    | ToggleRemoveData
    | ChangePriority String
    | ChangeLowpassCutoff String
    | ChangeYShift String
    | ChangeFieldEnding String
    | SendJson
    | Close


port jsonData : Json.Encode.Value -> Cmd msg


port removeModule : String -> Cmd msg


main : Program Never Model Msg
main =
    Html.program
        { init = default
        , view = \model -> Html.div [] (viewModel model)
        , update = updateModel
        , subscriptions = \_ -> Sub.none
        }


defaultModel : Model
defaultModel =
    { moduleName = "iq_demod"
    , className = "None"
    , active = False
    , priority = "1000"
    , plot = True
    , fieldEnding = "trace"
    , removeData = False
    , lowpassCutoff = "10000000.0"
    , yShift = "-8192.0"
    }


default : ( Model, Cmd Msg )
default =
    ( defaultModel, Cmd.none )


viewModel : Model -> List (Html Msg)
viewModel model =
    titleWithAttributions "IQ demodulation" model.active ToggleActive Close attributions
        ++ if model.active then
            [ integerField "Priority" model.priority ChangePriority
            , stringField "Process data field ending in" model.fieldEnding ChangeFieldEnding
            , floatField "Y-axis shift for data" model.yShift ChangeYShift
            , floatField "Plot lowpass cutoff frequency" model.lowpassCutoff ChangeLowpassCutoff
            , checkbox "Plot" model.plot TogglePlot
            , checkbox "Remove original data after processing" model.removeData ToggleRemoveData
            ]
           else
            [ Html.text "" ]


updateModel : Msg -> Model -> ( Model, Cmd Msg )
updateModel msg model =
    case msg of
        ToggleActive ->
            if model.active then
                updateModel SendJson { model | className = "None", active = False }
            else
                updateModel SendJson { model | className = "IQDemodulation", active = True }

        TogglePlot ->
            updateModel SendJson { model | plot = not model.plot }

        ToggleRemoveData ->
            updateModel SendJson { model | removeData = not model.removeData }

        ChangePriority newPriority ->
            updateModel SendJson { model | priority = newPriority }

        ChangeLowpassCutoff newCutoff ->
            updateModel SendJson { model | lowpassCutoff = newCutoff }

        ChangeYShift newShift ->
            updateModel SendJson { model | yShift = newShift }

        ChangeFieldEnding newEnding ->
            updateModel SendJson { model | fieldEnding = newEnding }

        SendJson ->
            ( model
            , jsonData
                (Json.Encode.list
                    [ Json.Encode.object
                        [ ( "module_name", Json.Encode.string model.moduleName )
                        , ( "class_name", Json.Encode.string model.className )
                        , ( "priority"
                          , Json.Encode.int
                                (ModuleHelpers.intDefault defaultModel.priority model.priority)
                          )
                        , ( "data_register"
                          , Json.Encode.list
                                (List.map Json.Encode.string
                                    [ "IQ-demodulation-data" ]
                                )
                          )
                        , ( "config"
                          , Json.Encode.object
                                [ ( "plot", Json.Encode.bool model.plot )
                                , ( "field_ending", Json.Encode.string model.fieldEnding )
                                , ( "remove_trace_data", Json.Encode.bool model.removeData )
                                , ( "lowpass_cutoff"
                                  , Json.Encode.float
                                        (ModuleHelpers.floatDefault defaultModel.lowpassCutoff model.lowpassCutoff)
                                  )
                                , ( "y_shift"
                                  , Json.Encode.float
                                        (ModuleHelpers.floatDefault defaultModel.yShift model.yShift)
                                  )
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
                clearInstrument ! [ sendJsonCmd, removeModule defaultModel.moduleName ]
