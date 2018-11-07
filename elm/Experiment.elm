module Experiment exposing (Experiment, decode, encode)

import Dict exposing (Dict)
import Json.Decode as D
import Json.Encode as E
import Plugin exposing (Plugin)


{-| Configuration data for a PLACE experiment.

This is very similar to the data saved into the `config.json` file.

-}
type alias Experiment =
    { title : String
    , directory : String
    , updates : Int
    , plugins : Dict String Plugin
    , comments : String
    }


decode : D.Decoder Experiment
decode =
    D.map5
        Experiment
        (D.field "title" D.string)
        (D.field "directory" D.string)
        (D.field "updates" D.int)
        (D.field "plugins" (D.dict Plugin.decode))
        (D.field "comments" D.string)


encode : Experiment -> E.Value
encode experiment =
    E.object
        [ ( "updates", E.int experiment.updates )
        , ( "plugins"
          , Dict.filter (\k v -> v.active) experiment.plugins
                |> Dict.map (\k v -> Plugin.encode v)
                |> Dict.toList
                |> E.object
          )
        , ( "title", E.string experiment.title )
        , ( "comments", E.string experiment.comments )
        ]
