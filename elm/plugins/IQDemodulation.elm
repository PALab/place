port module IQDemodulation exposing (main)

import Html exposing (Html)
import Html.Events
import Html.Attributes
import Json.Encode
import ModuleHelpers exposing (..)


type alias Model =
    { moduleName : String
    , className : String
    , active : Bool
    , priority : Int
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


port removeInstrument : String -> Cmd msg


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
    , priority = 1000
    , plot = True
    , fieldEnding = "trace"
    , removeData = False
    , lowpassCutoff = "10e6"
    , yShift = "-8192"
    }


default : ( Model, Cmd Msg )
default =
    ( defaultModel, Cmd.none )


viewModel : Model -> List (Html Msg)
viewModel model =
    title "IQ demodulation" model.active ToggleActive Close
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
            updateModel SendJson
                { model
                    | priority = Result.withDefault 1000 (String.toInt newPriority)
                }

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
                        , ( "priority", Json.Encode.int model.priority )
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
                                        (Result.withDefault 1.0e7
                                            (String.toFloat model.lowpassCutoff)
                                        )
                                  )
                                , ( "y_shift"
                                  , Json.Encode.float
                                        (Result.withDefault -8192.0
                                            (String.toFloat model.lowpassCutoff)
                                        )
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
                clearInstrument ! [ sendJsonCmd, removeInstrument defaultModel.moduleName ]
