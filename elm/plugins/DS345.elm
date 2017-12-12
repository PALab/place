port module DS345 exposing (main)

import Html exposing (Html)
import Html.Events
import Html.Attributes
import Json.Encode
import ModuleHelpers


type alias Model =
    { className : String
    , active : Bool
    , priority : Int
    }


type Msg
    = ToggleActive
    | ChangePriority String
    | SendJson
    | Close


port jsonData : Json.Encode.Value -> Cmd msg


port removeInstrument : String -> Cmd msg


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
    , priority = 10
    }


viewModel : Model -> List (Html Msg)
viewModel model =
    ModuleHelpers.title "DS345 Function Generator" model.active ToggleActive Close
        ++ if model.active then
            [ ModuleHelpers.integerField "Priority" model.priority ChangePriority ]
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
                        | className = "DS345"
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
                        [ ( "module_name", Json.Encode.string "ds345_function_gen" )
                        , ( "class_name", Json.Encode.string model.className )
                        , ( "priority", Json.Encode.int model.priority )
                        , ( "data_register", Json.Encode.list (List.map Json.Encode.string []) )
                        , ( "config"
                          , Json.Encode.object
                                []
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
                clearInstrument ! [ sendJsonCmd, removeInstrument "ds345_function_gen" ]
