port module Place exposing (main)

import Html exposing (Html)
import Json.Encode
import Experiment exposing (ExperimentMsg(..), defaultExperiment)
import Experiment.Model exposing (Experiment, Version)
import Experiment.View exposing (view)


port jsonData : (Json.Encode.Value -> msg) -> Sub msg


subscriptions : PlaceModel -> Sub PlaceMsg
subscriptions model =
    Sub.batch [ jsonData (\value -> PlaceMsg (UpdatePlugins value)) ]


main : Program Flags PlaceModel PlaceMsg
main =
    let
        initModel version =
            let
                numList =
                    String.split "," version

                major =
                    Result.withDefault 0 <| String.toInt <| Maybe.withDefault "0" <| List.head numList

                minor =
                    Result.withDefault 0 <| String.toInt <| Maybe.withDefault "0" <| List.head <| List.drop 1 numList

                revision =
                    Result.withDefault 0 <| String.toInt <| Maybe.withDefault "0" <| List.head <| List.drop 2 numList
            in
                PlaceModel { defaultExperiment | version = Version major minor revision } MainView
    in
        Html.programWithFlags
            { init = \flags -> update (PlaceMsg (GetStatus ())) (initModel flags.version)
            , view = \model -> Html.map PlaceMsg (view model.experiments)
            , update = update
            , subscriptions = subscriptions
            }


type alias Flags =
    { version : String }


type PlaceMsg
    = PlaceMsg ExperimentMsg


type View
    = MainView
    | NewView
    | ExperimentView Int
    | DatabaseView
    | SettingsView


type alias PlaceModel =
    { experiments : Experiment
    , currentView : View
    }


update : PlaceMsg -> PlaceModel -> ( PlaceModel, Cmd PlaceMsg )
update (PlaceMsg msg) model =
    let
        ( newModel, newCmd ) =
            Experiment.update msg model.experiments
    in
        ( PlaceModel newModel MainView, Cmd.none )
