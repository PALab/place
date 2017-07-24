port module PLACETemplate exposing (main)

import Html exposing (Html)
import Html.Events
import Html.Attributes
import Json.Encode


type alias Model =
    { moduleName : String
    , className : String
    , active : Bool
    , priority : Int
    }


type Msg
    = ToggleActive
    | ChangePriority String
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


defaultModel : Model
defaultModel =
    ( { moduleName = "place_template"
      , className = "None"
      , active = False
      , priority = 10
      }
    , Cmd.none
    )


viewModel : Model -> Html Msg
viewModel model =
    Html.div []
        ([ Html.h2 [] [ Html.text "Web interface template example" ] ]
            ++ [ Html.p []
                    [ Html.text "Active: "
                    , Html.input
                        [ Html.Attributes.type_ "checkbox"
                        , Html.Events.onClick ToggleActive
                        ]
                        []
                    ]
               ]
            ++ [ Html.p []
                    [ Html.text "Priority: "
                    , Html.input
                        [ Html.Attributes.value (toString model.priority)
                        , Html.Attributes.type_ "number"
                        , Html.Events.onInput ChangePriority
                        ]
                        []
                    ]
               ]
        )


updateModel : Msg -> Model -> ( Model, Cmd Msg )
updateModel msg model =
    case msg of
        ToggleActive ->
            if model.active then
                updateModel SendJson { model | className = "None", active = False }
            else
                updateModel SendJson { model | className = "PLACETemplate", active = True }

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
                        [ ( "module_name", Json.Encode.string model.moduleName )
                        , ( "class_name", Json.Encode.string model.className )
                        , ( "priority", Json.Encode.int model.priority )
                        , ( "config"
                          , Json.Encode.list
                                []
                          )
                        ]
                    ]
                )
            )
