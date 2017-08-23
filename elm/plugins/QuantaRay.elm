port module QuantaRay exposing (main)

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
    , power : Int
    , watchdog : Int
    }


type Msg
    = ToggleActive
    | ChangePriority String
    | ChangePower String
    | ChangeWatchdog String
    | SendJson


port jsonData : Json.Encode.Value -> Cmd msg


main : Program Never Model Msg
main =
    Html.program
        { init = defaultModel
        , view = \model -> Html.div [] (viewModel model)
        , update = updateModel
        , subscriptions = \_ -> Sub.none
        }


defaultModel : ( Model, Cmd Msg )
defaultModel =
    ( { moduleName = "quanta_ray"
      , className = "None"
      , active = False
      , priority = 0
      , power = 50
      , watchdog = 60
      }
    , Cmd.none
    )


viewModel : Model -> List (Html Msg)
viewModel model =
    title "QuantaRay INDI laser" model.active ToggleActive
        ++ if model.active then
            [ integerField "Priority" model.priority ChangePriority
            , integerField "Power" model.power ChangePower
            , integerField "Watchdog" model.watchdog ChangeWatchdog
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
                updateModel SendJson { model | className = "QuantaRayINDI", active = True }

        ChangePriority newPriority ->
            updateModel SendJson
                { model
                    | priority = Result.withDefault 0 (String.toInt newPriority)
                }

        ChangePower newPower ->
            updateModel SendJson
                { model
                    | power = Result.withDefault 50 (String.toInt newPower)
                }

        ChangeWatchdog newWatch ->
            updateModel SendJson
                { model
                    | watchdog = Result.withDefault 60 (String.toInt newWatch)
                }

        SendJson ->
            ( model
            , jsonData
                (Json.Encode.list
                    [ Json.Encode.object
                        [ ( "module_name", Json.Encode.string model.moduleName )
                        , ( "class_name", Json.Encode.string model.className )
                        , ( "priority", Json.Encode.int model.priority )
                        , ( "data_register", Json.Encode.list (List.map Json.Encode.string []) )
                        , ( "config"
                          , Json.Encode.object
                                [ ( "power_percentage", Json.Encode.int model.power )
                                , ( "watchdog_time", Json.Encode.int model.power )
                                ]
                          )
                        ]
                    ]
                )
            )
