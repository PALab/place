port module IQDemodulation exposing (main)

import Html exposing (Html)
import Html.Events
import Html.Attributes
import Json.Encode


type alias Model =
    { moduleName : String
    , className : String
    , active : Bool
    , priority : Int
    , plot : Bool
    , removeData : Bool
    , lowpassCutoff : String
    }


type Msg
    = ToggleActive
    | TogglePlot
    | ToggleRemoveData
    | ChangePriority String
    | ChangeLowpassCutoff String
    | SendJson


port jsonData : Json.Encode.Value -> Cmd msg


main : Program Never Model Msg
main =
    Html.program
        { init = defaultModel
        , view = viewModel
        , update = updateModel
        , subscriptions = \_ -> Sub.none
        }


defaultModel : ( Model, Cmd Msg )
defaultModel =
    ( { moduleName = "iq_demod"
      , className = "None"
      , active = False
      , priority = 1000
      , plot = True
      , removeData = False
      , lowpassCutoff = "10e6"
      }
    , Cmd.none
    )


viewModel : Model -> Html Msg
viewModel model =
    Html.div []
        ([ Html.h2 [] [ Html.text "IQ demodulation (Post-processing)" ] ]
            ++ [ Html.p []
                    [ Html.text "Active: "
                    , Html.input
                        [ Html.Attributes.type_ "checkbox"
                        , Html.Events.onClick ToggleActive
                        ]
                        []
                    ]
               ]
            ++ if model.active then
                [ Html.p []
                    [ Html.text "Priority: "
                    , Html.input
                        [ Html.Attributes.value (toString model.priority)
                        , Html.Attributes.type_ "number"
                        , Html.Events.onInput ChangePriority
                        ]
                        []
                    ]
                , Html.p []
                    [ Html.text "Plot lowpass cutoff frequency: "
                    , Html.input
                        [ Html.Attributes.value model.lowpassCutoff
                        , Html.Events.onInput ChangeLowpassCutoff
                        ]
                        []
                    , Html.br [] []
                    , Html.text "(this will not change the recorded data)"
                    ]
                , Html.p []
                    [ Html.text "Plot: "
                    , Html.input
                        [ Html.Attributes.type_ "checkbox"
                        , Html.Attributes.checked model.plot
                        , Html.Events.onClick TogglePlot
                        ]
                        []
                    ]
                , Html.p []
                    [ Html.text "Remove original data after processing: "
                    , Html.input
                        [ Html.Attributes.type_ "checkbox"
                        , Html.Attributes.checked model.removeData
                        , Html.Events.onClick ToggleRemoveData
                        ]
                        []
                    ]
                ]
               else
                [ Html.text "" ]
        )


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

        SendJson ->
            ( model
            , jsonData
                (Json.Encode.list
                    [ Json.Encode.object
                        [ ( "module_name", Json.Encode.string model.moduleName )
                        , ( "class_name", Json.Encode.string model.className )
                        , ( "priority", Json.Encode.int model.priority )
                        , ( "config"
                          , Json.Encode.object
                                [ ( "plot", Json.Encode.bool model.plot )
                                , ( "remove_trace_data", Json.Encode.bool model.removeData )
                                , ( "lowpass_cutoff", Json.Encode.float (
                                    Result.withDefault 10e6 (String.toFloat model.lowpassCutoff)))
                                ]
                          )
                        ]
                    ]
                )
            )
