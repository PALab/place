port module XPSControl exposing (main)

import Html exposing (Html)
import Html.Events
import Html.Attributes
import Json.Encode
import Result exposing (withDefault)
import ModuleHelpers


pythonModuleName =
    "xps_control"


type alias Stage =
    { name : String
    , priority : String
    , active : Bool
    , start : String
    , increment : String
    , end : String
    , wait : String
    }


defaultModel : Stage
defaultModel =
    { name = "None"
    , priority = "20"
    , active = False
    , start = "0.0"
    , increment = "0.5"
    , end = "calculate"
    , wait = "5.0"
    }


type Msg
    = ToggleActive
    | ChangeName String
    | ChangePriority String
    | ChangeStart String
    | ChangeIncrement String
    | ChangeEnd String
    | ChangeWait String
    | SendJson
    | Close


port jsonData : Json.Encode.Value -> Cmd msg


port removeModule : String -> Cmd msg


update : Msg -> Stage -> ( Stage, Cmd Msg )
update msg stage =
    case msg of
        ToggleActive ->
            if stage.active then
                update SendJson <| defaultModel
            else
                update SendJson { stage | active = True }

        ChangeName newValue ->
            update SendJson { stage | name = newValue }

        ChangePriority newValue ->
            update SendJson { stage | priority = newValue }

        ChangeStart newValue ->
            update SendJson { stage | start = newValue }

        ChangeIncrement newValue ->
            update SendJson { stage | increment = newValue, end = "calculate" }

        ChangeEnd newValue ->
            update SendJson { stage | increment = "calculate", end = newValue }

        ChangeWait newValue ->
            update SendJson { stage | wait = newValue }

        SendJson ->
            ( stage, jsonData <| toJson stage )

        Close ->
            let
                ( clearInstrument, sendJsonCmd ) =
                    update SendJson <| defaultModel
            in
                clearInstrument ! [ sendJsonCmd, removeModule "xps_control" ]


main =
    Html.program
        { init = ( defaultModel, Cmd.none )
        , view = \stage -> Html.div [] (view stage)
        , update = update
        , subscriptions = \_ -> Sub.none
        }


view : Stage -> List (Html Msg)
view stage =
    ModuleHelpers.title "XPS-controlled stages" stage.active ToggleActive Close
        ++ if stage.active then
            nameView stage
           else
            [ ModuleHelpers.empty ]


nameView : Stage -> List (Html Msg)
nameView stage =
    [ ModuleHelpers.dropDownBox "Name"
        stage.name
        ChangeName
        [ ( "None", "None" )
        , ( "ShortStage", "Short linear stage" )
        , ( "LongStage", "Long linear stage" )
        , ( "RotStage", "Rotational stage" )
        ]
    ]
        ++ (if stage.name == "None" then
                [ ModuleHelpers.empty ]
            else
                [ ModuleHelpers.integerField "Priority" stage.priority ChangePriority
                , ModuleHelpers.floatField "Start" stage.start ChangeStart
                , (if stage.increment == "calculate" then
                    ModuleHelpers.stringField "Increment" stage.increment ChangeIncrement
                   else
                    ModuleHelpers.floatField "Increment" stage.increment ChangeIncrement
                  )
                , (if stage.end == "calculate" then
                    ModuleHelpers.stringField "End" stage.end ChangeEnd
                   else
                    ModuleHelpers.floatField "End" stage.end ChangeEnd
                  )
                , ModuleHelpers.floatField "Wait time" stage.wait ChangeWait
                ]
           )


toJson : Stage -> Json.Encode.Value
toJson stage =
    Json.Encode.list
        [ Json.Encode.object
            [ ( "module_name", Json.Encode.string "xps_control" )
            , ( "class_name", Json.Encode.string stage.name )
            , ( "priority", Json.Encode.int (ModuleHelpers.intDefault defaultModel.priority stage.priority) )
            , ( "data_register"
              , Json.Encode.list
                    (List.map Json.Encode.string [ stage.name ++ "-position" ])
              )
            , ( "config"
              , Json.Encode.object
                    [ ( "start"
                      , Json.Encode.float
                            (case String.toFloat stage.start of
                                Ok num ->
                                    num

                                otherwise ->
                                    0.0
                            )
                      )
                    , if stage.end == "calculate" then
                        ( "increment"
                        , Json.Encode.float
                            (case String.toFloat stage.increment of
                                Ok num ->
                                    num

                                otherwise ->
                                    1.0
                            )
                        )
                      else
                        ( "end"
                        , Json.Encode.float
                            (case String.toFloat stage.end of
                                Ok num ->
                                    num

                                otherwise ->
                                    1.0
                            )
                        )
                    , ( "wait", Json.Encode.float (ModuleHelpers.floatDefault defaultModel.wait stage.wait) )
                    ]
              )
            ]
        ]


{-| Helper function to present an option in a drop-down selection box.
-}
anOption : String -> String -> String -> Html Msg
anOption str val disp =
    Html.option
        [ Html.Attributes.value val, Html.Attributes.selected (str == val) ]
        [ Html.text disp ]
