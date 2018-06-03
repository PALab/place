module Place.Model exposing (Model, Msg(..), PlacePlugin)

import Html exposing (Html)
import Http
import Json.Encode


type alias Model =
    { modules : List PlacePlugin
    , directory : String
    , updates : Int
    , comments : String
    , plotData : Html Msg
    , showJson : Bool
    , showData : Bool
    , version : String
    , ready : String
    }


type alias PlacePlugin =
    { module_name : String
    , className : String
    , priority : Int
    , dataRegister : List String
    , config : Json.Encode.Value
    }


type Msg
    = ChangeDirectory String
    | ChangeUpdates String
    | ChangeShowJson Bool
    | ChangeShowData Bool
    | ChangeComments String
    | PostResponse (Result Http.Error String)
    | UpdateModules Json.Encode.Value
    | StartExperiment
    | GetStatus ()
    | StatusResponse (Result Http.Error String)
