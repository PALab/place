port module QuantaRay exposing (main)

import Html exposing (Html)
import Json.Encode
import ModuleHelpers exposing (..)


attributions : ModuleHelpers.Attributions
attributions =
    { authors = [ "Jonathan Simpson", "Paul Freeman" ]
    , maintainer = "Jonathan Simpson"
    , maintainerEmail = "jsim921@aucklanduni.ac.nz"
    }


type alias Model =
    { moduleName : String
    , className : String
    , active : Bool
    , priority : String
    , power : String
    , watchdog : String
    , progress : Maybe Json.Encode.Value
    }


type Msg
    = ToggleActive
    | ChangePriority String
    | ChangePower String
    | ChangeWatchdog String
    | SendJson
    | UpdateProgress Json.Encode.Value
    | Close


port config : Json.Encode.Value -> Cmd msg


port processProgress : (Json.Encode.Value -> msg) -> Sub msg


port removeModule : String -> Cmd msg


main : Program Never Model Msg
main =
    Html.program
        { init = default
        , view = \model -> Html.div [] (viewModel model)
        , update = updateModel
        , subscriptions = always <| processProgress UpdateProgress
        }


defaultModel : Model
defaultModel =
    { moduleName = "quanta_ray"
    , className = "None"
    , active = False
    , priority = "0"
    , power = "50"
    , watchdog = "60"
    , progress = Nothing
    }


default : ( Model, Cmd Msg )
default =
    ( defaultModel, Cmd.none )


viewModel : Model -> List (Html Msg)
viewModel model =
    titleWithAttributions "QuantaRay INDI laser" model.active ToggleActive Close attributions
        ++ if model.active then
            [ integerField "Priority" model.priority ChangePriority
            , integerField "Power" model.power ChangePower
            , integerField "Watchdog" model.watchdog ChangeWatchdog
            , displayAllProgress model.progress
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
            , config
                (Json.Encode.list
                    [ Json.Encode.object
                        [ ( "python_module_name", Json.Encode.string model.moduleName )
                        , ( "python_class_name", Json.Encode.string model.className )
                        , ( "elm_module_name", Json.Encode.string "QuantaRay" )
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

        UpdateProgress progress ->
            ( { model | progress = Just progress }, Cmd.none )

        Close ->
            let
                ( clearInstrument, sendJsonCmd ) =
                    updateModel SendJson defaultModel
            in
                clearInstrument ! [ sendJsonCmd, removeModule "QuantaRay" ]
