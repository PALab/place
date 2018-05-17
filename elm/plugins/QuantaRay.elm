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
    , priority : String
    , power : String
    , watchdog : String
    }


type Msg
    = ToggleActive
    | ChangePriority String
    | ChangePower String
    | ChangeWatchdog String
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
    { moduleName = "quanta_ray"
    , className = "None"
    , active = False
    , priority = "0"
    , power = "50"
    , watchdog = "60"
    }


default : ( Model, Cmd Msg )
default =
    ( defaultModel, Cmd.none )


viewModel : Model -> List (Html Msg)
viewModel model =
    title "QuantaRay INDI laser" model.active ToggleActive Close
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
                { model | priority = newPriority }

        ChangePower newPower ->
            updateModel SendJson
                { model | power = newPower }

        ChangeWatchdog newWatch ->
            updateModel SendJson
                { model | watchdog = newWatch }

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
                        , ( "data_register", Json.Encode.list (List.map Json.Encode.string []) )
                        , ( "config"
                          , Json.Encode.object
                                [ ( "power_percentage"
                                  , Json.Encode.int
                                        (ModuleHelpers.intDefault defaultModel.power model.power)
                                  )
                                , ( "watchdog_time"
                                  , Json.Encode.int
                                        (ModuleHelpers.intDefault defaultModel.watchdog model.watchdog)
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
                    updateModel SendJson defaultModel
            in
                clearInstrument ! [ sendJsonCmd, removeModule "quanta_ray" ]
