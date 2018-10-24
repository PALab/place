module Plugin exposing (Plugin, decode, encode)

import Json.Decode as D
import Json.Encode as E
import Metadata exposing (Metadata)


type alias Plugin =
    { active : Bool
    , priority : Int
    , metadata : Metadata
    , config : E.Value
    , progress : E.Value
    }


decode : D.Decoder Plugin
decode =
    D.map5
        Plugin
        (D.field "active" D.bool)
        (D.field "priority" D.int)
        (D.field "metadata" Metadata.decode)
        (D.field "config" D.value)
        (D.field "progress" D.value)


encode : Plugin -> E.Value
encode plugin =
    E.object
        [ ( "active", E.bool plugin.active )
        , ( "priority", E.int plugin.priority )
        , ( "metadata", Metadata.encode plugin.metadata )
        , ( "config", plugin.config )
        , ( "progress", plugin.progress )
        ]
