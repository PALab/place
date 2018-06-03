port module Place exposing (main)

import String
import Time
import Task
import Process
import Http
import Html exposing (Html)
import Html.Attributes
import Json.Decode
import Json.Encode
import Place.Model exposing (Model, Msg(..), PlacePlugin)
import Place.View exposing (view)
import Place.Encode
import Place.State exposing (update)


port jsonData : (Json.Encode.Value -> msg) -> Sub msg


subscriptions : Model -> Sub Msg
subscriptions experiment =
    Sub.batch [ jsonData UpdateModules ]


main : Program Flags Model Msg
main =
    Html.programWithFlags
        { init = \flags -> update (GetStatus ()) { experimentDefaultState | version = flags.version }
        , view = view
        , update = update
        , subscriptions = subscriptions
        }


type alias Flags =
    { version : String }


experimentDefaultState : Model
experimentDefaultState =
    { modules = []
    , directory = "/tmp/place_tmp"
    , updates = 1
    , comments = ""
    , plotData = Html.text ""
    , showJson = False
    , showData = False
    , version = "0.0.0"
    , ready = "PLACE loading"
    }
