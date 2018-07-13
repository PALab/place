port module Place exposing (main)

import Html exposing (Html)
import Html.Attributes
import Json.Encode
import Place.Experiment
import Place.History


port pluginConfig : (Json.Encode.Value -> msg) -> Sub msg


type alias Model =
    { experiment : Place.Experiment.Model
    , history : Place.History.Model
    , currentView : View
    , version : Version
    }


type View
    = Experiment
    | History


type Msg
    = ExperimentMsg Place.Experiment.Msg
    | HistoryMsg Place.History.Msg


main : Program Flags Model Msg
main =
    Html.programWithFlags
        { init =
            \flags ->
                update (ExperimentMsg Place.Experiment.GetStatus) <|
                    { experiment = Place.Experiment.init
                    , history = Place.History.init
                    , currentView = Experiment
                    , version = (Version 0 0 0)
                    }
        , view = view
        , update = update
        , subscriptions = subscriptions
        }


type alias Version =
    { major : Int
    , minor : Int
    , revision : Int
    }


type alias Flags =
    { version : String }


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        ExperimentMsg experimentMsg ->
            let
                ( experimentModel, experimentCmd ) =
                    Place.Experiment.update experimentMsg model.experiment
            in
                ( { model | experiment = experimentModel }, Cmd.map ExperimentMsg experimentCmd )

        HistoryMsg historyMsg ->
            case historyMsg of
                Place.History.NewExperiment ->
                    ( { model | currentView = Experiment }, Cmd.none )


view : Model -> Html Msg
view model =
    case model.currentView of
        Experiment ->
            Html.div [ Html.Attributes.class "experimentView" ]
                [ Html.map ExperimentMsg <| Place.Experiment.view model.experiment ]

        History ->
            Html.div [ Html.Attributes.class "historyView" ]
                [ Html.map HistoryMsg <| Place.History.view model.history ]



--loaderView : Model -> Html Msg
--loaderView model =
--    Html.div []
--        [ Html.p [ Html.Attributes.class "loaderTitle" ] [ Html.text "PLACE is busy" ]
--        , Html.div [ Html.Attributes.class "loader" ] []
--        , Html.p [ Html.Attributes.class "progresstext" ] [ Html.text (toString model.status) ]
--        ]


subscriptions : Model -> Sub Msg
subscriptions model =
    Sub.batch [ pluginConfig (\value -> ExperimentMsg (Place.Experiment.UpdatePlugins value)) ]
