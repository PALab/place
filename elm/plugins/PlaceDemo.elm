port module PlaceDemo exposing (view)

import Html exposing (Html)
import Json.Encode
import ModuleHelpers


attributions : ModuleHelpers.Attributions
attributions =
    { authors = [ "Paul Freeman" ]
    , maintainer = "Paul Freeman"
    , maintainerEmail = "paul.freeman.cs@gmail.com"
    }


main : Program Never Model Msg
main =
    Html.program
        { init = ( Model False "10" "128" "1.0" True Nothing, Cmd.none )
        , view = view
        , update = update
        , subscriptions = always <| processProgress UpdateProgress
        }


type alias Model =
    { active : Bool
    , priority : String
    , points : String
    , sleep : String
    , plot : Bool
    , progress : Maybe Json.Encode.Value
    }


type Msg
    = ChangePriority String
    | ChangeSleep String
    | ChangePoints String
    | TogglePlot
    | ToggleActive
    | SendJson
    | UpdateProgress Json.Encode.Value
    | Close


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        ChangePriority newValue ->
            update SendJson { model | priority = newValue }

        ChangeSleep newValue ->
            update SendJson { model | sleep = newValue }

        ChangePoints newValue ->
            update SendJson { model | points = newValue }

        TogglePlot ->
            update SendJson { model | plot = not model.plot }

        ToggleActive ->
            update SendJson { model | active = not model.active }

        SendJson ->
            ( model, config (toJson model) )

        UpdateProgress progress ->
            ( { model | progress = Just progress }, Cmd.none )

        Close ->
            close model


view : Model -> Html Msg
view model =
    Html.div [] <|
        ModuleHelpers.titleWithAttributions "PLACE Demo Instrument" model.active ToggleActive Close attributions
            ++ if model.active then
                [ ModuleHelpers.integerField "Priority" model.priority ChangePriority
                , ModuleHelpers.integerField "Number of Points" model.points ChangePoints
                , ModuleHelpers.floatField "Sleep time between updates" model.sleep ChangeSleep
                , ModuleHelpers.checkbox "Get plots during execution" model.plot TogglePlot
                , ModuleHelpers.displayAllProgress model.progress
                ]
               else
                [ Html.text ""
                ]


port config : Json.Encode.Value -> Cmd msg


toJson : Model -> Json.Encode.Value
toJson model =
    Json.Encode.list
        [ Json.Encode.object
            [ ( "python_module_name", Json.Encode.string "place_demo" )
            , ( "python_class_name"
              , Json.Encode.string
                    (if model.active then
                        "PlaceDemo"
                     else
                        "None"
                    )
              )
            , ( "elm_module_name", Json.Encode.string "PlaceDemo" )
            , ( "priority", Json.Encode.int <| ModuleHelpers.intDefault "10" model.priority )
            , ( "data_register"
              , Json.Encode.list
                    (List.map Json.Encode.string
                        [ "PlaceDemo-count", "PlaceDemo-trace" ]
                    )
              )
            , ( "config"
              , Json.Encode.object
                    [ ( "sleep_time", Json.Encode.float <| ModuleHelpers.floatDefault "1.0" model.sleep )
                    , ( "number_of_points", Json.Encode.int <| ModuleHelpers.intDefault "128" model.points )
                    , ( "plot", Json.Encode.bool model.plot )
                    ]
              )
            ]
        ]


port removeModule : String -> Cmd msg


port processProgress : (Json.Encode.Value -> msg) -> Sub msg


close : Model -> ( Model, Cmd Msg )
close model =
    let
        ( clearInstrument, sendJsonCmd ) =
            update SendJson <| Model False "10" "128" "1.0" True Nothing
    in
        clearInstrument ! [ sendJsonCmd, removeModule "PlaceDemo" ]
