port module Place exposing (main)

import Html exposing (Html)
import Json.Encode
import Place.Model exposing (Model, Msg(..), PlacePlugin, defaultExperiment)
import Place.View exposing (view)
import Place.State exposing (update)


port jsonData : (Json.Encode.Value -> msg) -> Sub msg


subscriptions : Model -> Sub Msg
subscriptions experiment =
    Sub.batch [ jsonData UpdateModules ]


main : Program Flags Model Msg
main =
    let
        initModel =
            Place.Model.defaultExperiment
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
