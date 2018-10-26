module Metadata exposing (Metadata, decode, default, encode)

import Json.Decode as D
import Json.Encode as E


type alias Metadata =
    { title : String
    , authors : List String
    , maintainer : String
    , email : String
    , url : String
    , elm : { moduleName : String }
    , python : { moduleName : String, className : String }
    , defaultPriority : String
    }


default : Metadata
default =
    { title = "no title"
    , authors = [ "no authers" ]
    , maintainer = "unmaintainted"
    , email = "no email"
    , url = "no url"
    , elm = { moduleName = "unknown Elm module" }
    , python = { moduleName = "unknown Python module", className = "unknown Python class" }
    , defaultPriority = "10"
    }


decode : D.Decoder Metadata
decode =
    D.oneOf
        [ D.null default
        , D.map8
            Metadata
            (D.field "title" D.string)
            (D.field "authors" <| D.list D.string)
            (D.field "maintainer" D.string)
            (D.field "email" D.string)
            (D.field "url" D.string)
            (D.field "elm_module_name" D.string
                |> D.andThen (D.succeed << (\name -> { moduleName = name }))
            )
            (D.field "python_module_name" D.string
                |> D.andThen
                    (\moduleName ->
                        D.field "python_class_name" D.string
                            |> D.andThen
                                (\className ->
                                    D.succeed { moduleName = moduleName, className = className }
                                )
                    )
            )
            (D.field "default_priority" D.string)
        ]


encode : Metadata -> E.Value
encode metadata =
    E.object
        [ ( "title", E.string metadata.title )
        , ( "authors", E.list <| List.map E.string metadata.authors )
        , ( "maintainer", E.string metadata.maintainer )
        , ( "email", E.string metadata.email )
        , ( "url", E.string metadata.url )
        , ( "elm_module_name", E.string metadata.elm.moduleName )
        , ( "python_module_name", E.string metadata.python.moduleName )
        , ( "python_class_name", E.string metadata.python.className )
        , ( "default_priority", E.string metadata.defaultPriority )
        ]
