port module Tektronix exposing (main)

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
    , forceTrigger : Bool
    , recordLength : Int
    }


type Msg
    = ToggleActive
    | TogglePlot
    | ToggleTrigger
    | ChangePriority String
    | ChangeLength String
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
    ( { moduleName = "tektronix"
      , className = "None"
      , active = False
      , priority = 100
      , plot = False
      , forceTrigger = True
      , recordLength = 10000
      }
    , Cmd.none
    )


viewModel : Model -> Html Msg
viewModel model =
    Html.div []
        ([ Html.h2 [] [ Html.text "Tektronix DP03014 oscilloscope" ] ]
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
                    [ Html.text "Plot: "
                    , Html.input
                        [ Html.Attributes.type_ "checkbox"
                        , Html.Events.onClick TogglePlot
                        ]
                        []
                    ]
                , Html.p []
                    [ Html.text "Samples: "
                    , Html.select [ Html.Events.onInput ChangeLength ]
                        [ Html.option
                            [ Html.Attributes.value "1000"
                            , Html.Attributes.selected (model.recordLength == 1000)
                            ]
                            [ Html.text "1K" ]
                        , Html.option
                            [ Html.Attributes.value "10000"
                            , Html.Attributes.selected (model.recordLength == 10000)
                            ]
                            [ Html.text "10K" ]
                        , Html.option
                            [ Html.Attributes.value "100000"
                            , Html.Attributes.selected (model.recordLength == 100000)
                            ]
                            [ Html.text "100K" ]
                        , Html.option
                            [ Html.Attributes.value "1000000"
                            , Html.Attributes.selected (model.recordLength == 1000000)
                            ]
                            [ Html.text "1M" ]
                        , Html.option
                            [ Html.Attributes.value "5000000"
                            , Html.Attributes.selected (model.recordLength == 5000000)
                            ]
                            [ Html.text "5M" ]
                        ]
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
                updateModel SendJson { model | className = "DPO3014", active = True }

        TogglePlot ->
            updateModel SendJson { model | plot = not model.plot }

        ToggleTrigger ->
            updateModel SendJson { model | forceTrigger = not model.forceTrigger }

        ChangePriority newPriority ->
            updateModel SendJson
                { model
                    | priority = Result.withDefault 100 (String.toInt newPriority)
                }

        ChangeLength newLength ->
            updateModel SendJson
                { model
                    | recordLength = Result.withDefault 10000 (String.toInt newLength)
                }

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
                                (List.map Json.Encode.string [ model.className ++ "-trace" ])
                          )
                        , ( "config"
                          , Json.Encode.object
                                [ ( "plot", Json.Encode.bool model.plot )
                                , ( "force_trigger", Json.Encode.bool False )
                                , ( "record_length", Json.Encode.int model.recordLength )
                                ]
                          )
                        ]
                    ]
                )
            )
