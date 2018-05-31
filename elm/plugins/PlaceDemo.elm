port module PlaceDemo exposing (view)

import Html exposing (Html)
import Html.Events
import Html.Attributes
import Json.Encode
import Result exposing (withDefault)
import ModuleHelpers


attributions : ModuleHelpers.Attributions
attributions =
    { authors = [ "Paul Freeman" ]
    , maintainer = "Paul Freeman"
    , maintainerEmail = "paul.freeman.cs@gmail.com"
    }


main =
    Html.program
        { init = init
        , view = view
        , update = update
        , subscriptions = subscriptions
        }


initModel : Model
initModel =
    { active = False
    , priority = 10
    , sleep = 1.0
    , plot = True
    }


init : ( Model, Cmd msg )
init =
    ( initModel, Cmd.none )


type alias Model =
    { active : Bool
    , priority : Int
    , sleep : Float
    , plot : Bool
    }


view : Model -> Html Msg
view model =
    Html.div [] <| mainView model


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        ChangePriority newValue ->
            changePriority newValue model

        ChangeSleep newValue ->
            changeSleep newValue model

        PlotSwitch yesOrNo ->
            plotSwitch yesOrNo model

        ToggleActive ->
            toggleActive model

        SendJson ->
            sendJson model

        Close ->
            close model


type Msg
    = ChangePriority String
    | ChangeSleep String
    | PlotSwitch String
    | ToggleActive
    | SendJson
    | Close


subscriptions : Model -> Sub msg
subscriptions model =
    Sub.none


mainView : Model -> List (Html Msg)
mainView model =
    ModuleHelpers.titleWithAttributions "PLACE Demo Instrument" model.active ToggleActive Close attributions
        ++ if model.active then
            [ Html.p [] (priorityView model)
            , Html.p [] (sleepView model)
            , Html.p [] (plotView model)
            ]
           else
            [ Html.text ""
            ]


priorityView model =
    [ Html.text "Priority: "
    , Html.input
        [ Html.Attributes.value <| toString model.priority
        , Html.Attributes.type_ "number"
        , Html.Events.onInput ChangePriority
        ]
        []
    ]


sleepView model =
    [ Html.text "Sleep: "
    , Html.input
        [ Html.Attributes.value <| toString model.sleep
        , Html.Attributes.type_ "number"
        , Html.Attributes.step "0.001"
        , Html.Events.onInput ChangeSleep
        ]
        []
    ]


plotView model =
    [ Html.text "Plot: "
    , Html.select [ Html.Events.onInput PlotSwitch ]
        [ Html.option
            [ Html.Attributes.value "No"
            , Html.Attributes.selected (not model.plot)
            ]
            [ Html.text "No" ]
        , Html.option
            [ Html.Attributes.value "Yes"
            , Html.Attributes.selected model.plot
            ]
            [ Html.text "Yes" ]
        ]
    ]


toggleActive model =
    let
        newCounterModel =
            { model | active = not model.active }
    in
        update SendJson newCounterModel


changePriority newValue model =
    update SendJson { model | priority = withDefault 10 (String.toInt newValue) }


changeSleep newValue model =
    update SendJson { model | sleep = withDefault 1.0 <| String.toFloat newValue }


plotSwitch yesOrNo model =
    update SendJson { model | plot = (yesOrNo == "Yes") }


sendJson model =
    ( model, jsonData (toJson model) )


port jsonData : Json.Encode.Value -> Cmd msg


toJson model =
    Json.Encode.list
        [ Json.Encode.object
            [ ( "module_name", Json.Encode.string "place_demo" )
            , ( "class_name"
              , Json.Encode.string
                    (if model.active then
                        "PlaceDemo"
                     else
                        "None"
                    )
              )
            , ( "priority", Json.Encode.int model.priority )
            , ( "data_register"
              , Json.Encode.list
                    (List.map Json.Encode.string
                        [ "PlaceDemo-count", "PlaceDemo-trace" ]
                    )
              )
            , ( "config"
              , Json.Encode.object
                    [ ( "sleep_time", Json.Encode.float model.sleep )
                    , ( "plot", Json.Encode.bool model.plot )
                    ]
              )
            ]
        ]


port removeModule : String -> Cmd msg


close model =
    let
        ( clearInstrument, sendJsonCmd ) =
            update SendJson <| initModel
    in
        clearInstrument ! [ sendJsonCmd, removeModule "PlaceDemo" ]
