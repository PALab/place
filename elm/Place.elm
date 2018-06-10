port module Place exposing (main)

import Html exposing (Html)
import Json.Encode
import Place.Experiment exposing (Experiment, ExperimentMsg(..), defaultExperiment)
import Place.View exposing (view)
import Place.State exposing (update)


port jsonData : (Json.Encode.Value -> msg) -> Sub msg


subscriptions : Experiment -> Sub ExperimentMsg
subscriptions experiment =
    Sub.batch [ jsonData UpdateModules ]


main : Program Flags Experiment ExperimentMsg
main =
    let
        initModel =
            defaultExperiment
    in
        Html.programWithFlags
            { init = \flags -> update (GetStatus ()) { initModel | version = flags.version }
            , view = view
            , update = update
            , subscriptions = subscriptions
            }


type alias Flags =
    { version : String }


type View
    = MainView
    | NewView
    | ExperimentView Experiment
    | DatabaseView
    | SettingsView


type alias PlaceModel =
    { view : View
    }
