port module Place exposing (main)

import Html exposing (Html)
import Json.Encode
import Experiment exposing (Model, Msg(..))


port jsonData : (Json.Encode.Value -> msg) -> Sub msg


type alias Model =
    { experiment : Experiment.Model
    , currentView : View
    , version : Version
    }


default : Model
default =
    { experiment = Experiment.default
    , currentView = New
    , version = Version 0 0 0
    }


type View
    = Main
    | New
    | Experiment Int
    | Database
    | Settings


type Msg
    = ExperimentMsg Experiment.Msg


main : Program Flags Model Msg
main =
    Html.programWithFlags
        { init = \flags -> update (ExperimentMsg (GetStatus ())) default
        , view = view
        , update = update
        , subscriptions = subscriptions
        }


view : Model -> Html Msg
view model =
    case model.currentView of
        Main ->
            Html.text "PLACE Main View"

        New ->
            Html.map ExperimentMsg <| Experiment.view model.experiment

        Experiment number ->
            Html.text <| "PLACE Experiment " ++ toString number ++ " View"

        Database ->
            Html.text "PLACE Database View"

        Settings ->
            Html.text "PLACE Settings View"


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
                    Experiment.update experimentMsg model.experiment
            in
                ( { model | experiment = experimentModel }, Cmd.map ExperimentMsg experimentCmd )


subscriptions : Model -> Sub Msg
subscriptions model =
    Sub.batch [ jsonData (\value -> ExperimentMsg (UpdatePlugins value)) ]
