port module Tektronix exposing (Model, Msg, default, updateModel, viewModel)

import Html exposing (Html)
import Html.Events
import Html.Attributes
import Json.Encode
import ModuleHelpers exposing (..)


attributions : ModuleHelpers.Attributions
attributions =
    { authors = [ "Paul Freeman" ]
    , maintainer = "Paul Freeman"
    , maintainerEmail = "pfre484@aucklanduni.ac.nz"
    }


type alias Model =
    { moduleName : String
    , className : String
    , active : Bool
    , priority : String
    , plot : Bool
    , forceTrigger : Bool
    }


type Msg
    = ToggleActive
    | TogglePlot
    | ToggleTrigger
    | ChangePriority String
    | SendJson
    | Close


port jsonData : Json.Encode.Value -> Cmd msg


port removeModule : String -> Cmd msg


default : ( Model, Cmd Msg )
default =
    ( defaultModel
    , Cmd.none
    )


defaultModel : Model
defaultModel =
    { moduleName = "tektronix"
    , className = "None"
    , active = False
    , priority = "100"
    , plot = False
    , forceTrigger = True
    }


viewModel : String -> Model -> List (Html Msg)
viewModel name model =
    titleWithAttributions ("Tektronix " ++ name ++ " oscilloscope") model.active ToggleActive Close attributions
        ++ if model.active then
            [ integerField "Priority" model.priority ChangePriority
            , checkbox "Plot" model.plot TogglePlot
            ]
           else
            [ Html.text "" ]


updateModel : String -> String -> Msg -> Model -> ( Model, Cmd Msg )
updateModel name mod msg model =
    let
        up =
            updateModel name mod SendJson
    in
        case msg of
            ToggleActive ->
                if model.active then
                    up { model | className = "None", active = False }
                else
                    up { model | className = name, active = True }

            TogglePlot ->
                up { model | plot = not model.plot }

            ToggleTrigger ->
                up { model | forceTrigger = not model.forceTrigger }

            ChangePriority newPriority ->
                up { model | priority = newPriority }

            SendJson ->
                ( model
                , jsonData
                    (Json.Encode.list
                        [ Json.Encode.object
                            [ ( "module_name", Json.Encode.string model.moduleName )
                            , ( "class_name", Json.Encode.string model.className )
                            , ( "priority", Json.Encode.int (ModuleHelpers.intDefault defaultModel.priority model.priority) )
                            , ( "data_register"
                              , Json.Encode.list
                                    (List.map Json.Encode.string [ model.className ++ "-trace" ])
                              )
                            , ( "config"
                              , Json.Encode.object
                                    [ ( "plot", Json.Encode.bool model.plot )
                                    , ( "force_trigger", Json.Encode.bool False )
                                    ]
                              )
                            ]
                        ]
                    )
                )

            Close ->
                let
                    ( clearInstrument, sendJsonCmd ) =
                        up defaultModel
                in
                    clearInstrument ! [ sendJsonCmd, removeModule ("Tektronix" ++ name) ]
