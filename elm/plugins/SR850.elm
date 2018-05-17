port module SR850 exposing (main)

import Html exposing (Html)
import Html.Events
import Html.Attributes
import Json.Encode
import ModuleHelpers


attributions : ModuleHelpers.Attributions
attributions =
    { authors = [ "Paul Freeman" ]
    , maintainer = "Paul Freeman"
    , maintainerEmail = "pfre484@aucklanduni.ac.nz"
    }


type alias Model =
    { className : String
    , active : Bool
    , priority : String
    }


type Msg
    = ToggleActive
    | ChangePriority String
    | SendJson
    | Close


port jsonData : Json.Encode.Value -> Cmd msg


port removeModule : String -> Cmd msg


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
    , priority = "10"
    }


viewModel : Model -> List (Html Msg)
viewModel model =
    ModuleHelpers.titleWithAttributions "SR850 Lock-In Amplifier" model.active ToggleActive Close attributions
        ++ if model.active then
            [ ModuleHelpers.integerField "Priority" model.priority ChangePriority ]
           else
            [ ModuleHelpers.empty ]


updateModel : Msg -> Model -> ( Model, Cmd Msg )
updateModel msg model =
    case msg of
        ToggleActive ->
            if model.active then
                updateModel SendJson { model | className = "None", active = False }
            else
                updateModel SendJson { model | className = "SR850", active = True }

        ChangePriority newPriority ->
            updateModel SendJson { model | priority = newPriority }

        SendJson ->
            ( model
            , jsonData
                (Json.Encode.list
                    [ Json.Encode.object
                        [ ( "module_name", Json.Encode.string "sr850_amp" )
                        , ( "class_name", Json.Encode.string model.className )
                        , ( "priority", Json.Encode.int (ModuleHelpers.intDefault defaultModel.priority model.priority) )
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
                clearInstrument ! [ sendJsonCmd, removeModule "sr850_amp" ]
