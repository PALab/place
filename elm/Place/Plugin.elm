module Place.Plugin exposing (Plugin)


type alias Plugin =
    { module_name : String
    , className : String
    , priority : Int
    , dataRegister : List String
    , config : Json.Encode.Value
    }
