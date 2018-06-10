module Place.Encode exposing (toJson, toString)

import Json.Encode
import Place.Experiment exposing (Experiment)
import Place.Plugin exposing (Plugin)


toJson : Experiment -> Json.Encode.Value
toJson experiment =
    Json.Encode.object
        [ ( "updates", Json.Encode.int experiment.updates )
        , ( "directory", Json.Encode.string experiment.directory )
        , ( "comments", Json.Encode.string experiment.comments )
        , ( "modules", encodePluginsToJson experiment.modules )
        ]


toString : Experiment -> String
toString =
    toJson >> Json.Encode.encode 4


encodePluginsToJson : List Plugin -> Json.Encode.Value
encodePluginsToJson =
    List.map encodePluginToJson >> Json.Encode.list


encodePluginToJson : Plugin -> Json.Encode.Value
encodePluginToJson plugin =
    Json.Encode.object
        [ ( "module_name", Json.Encode.string plugin.module_name )
        , ( "class_name", Json.Encode.string plugin.className )
        , ( "priority", Json.Encode.int plugin.priority )
        , ( "config", plugin.config )
        ]
