port module H5Output exposing (main)

import Html exposing (Html)
import Html.Events
import Html.Attributes
import Json.Encode
import ModuleHelpers


type alias Model =
    { className : String
    , active : Bool
    , traceField : String
    , xField : String
    , yField : String
    , thetaField : String
    }


type Msg
    = ToggleActive
    | ChangeTraceField String
    | ChangeXField String
    | ChangeYField String
    | ChangeThetaField String
    | SendJson


port jsonData : Json.Encode.Value -> Cmd msg


main : Program Never Model Msg
main =
    Html.program
        { init = ( defaultModel, Cmd.none )
        , view = \model -> Html.div [] (viewModel model)
        , update = updateModel
        , subscriptions = \_ -> Sub.none
        }


defaultModel : Model
defaultModel =
    { className = "None"
    , active = False
    , traceField = ""
    , xField = ""
    , yField = ""
    , thetaField = ""
    }


viewModel : Model -> List (Html Msg)
viewModel model =
    ModuleHelpers.title "PAL H5 output" model.active ToggleActive
        ++ if model.active then
            [ ModuleHelpers.stringField "trace field" model.traceField ChangeTraceField
            , ModuleHelpers.stringField "x-position field" model.xField ChangeXField
            , ModuleHelpers.stringField "y-position field" model.yField ChangeYField
            , ModuleHelpers.stringField "theta-position field" model.thetaField ChangeThetaField
            ]
           else
            [ ModuleHelpers.empty ]


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
                        | className = "H5Output"
                        , active = True
                    }

        ChangeTraceField newField ->
            updateModel SendJson { model | traceField = newField }

        ChangeXField newField ->
            updateModel SendJson { model | xField = newField }

        ChangeYField newField ->
            updateModel SendJson { model | yField = newField }

        ChangeThetaField newField ->
            updateModel SendJson { model | thetaField = newField }

        SendJson ->
            ( model
            , jsonData
                (Json.Encode.list
                    [ Json.Encode.object
                        [ ( "module_name", Json.Encode.string "h5_output" )
                        , ( "class_name", Json.Encode.string model.className )
                        , ( "priority", Json.Encode.int 9999 )
                        , ( "data_register", Json.Encode.list (List.map Json.Encode.string []) )
                        , ( "config"
                          , Json.Encode.object
                                [ ( "trace_field", Json.Encode.string model.traceField )
                                , ( "x_position_field", Json.Encode.string model.xField )
                                , ( "y_position_field", Json.Encode.string model.yField )
                                , ( "theta_position_field", Json.Encode.string model.thetaField )
                                ]
                          )
                        ]
                    ]
                )
            )
