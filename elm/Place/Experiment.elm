module Place.Experiment exposing (Experiment, ExperimentMsg(..), Status(..), defaultExperiment)

import Http
import Dict exposing (Dict)
import Json.Encode
import Place.Plugin exposing (Plugin)


type Status
    = New
    | Started
    | Running
    | Complete
    | Error


type alias Experiment =
    { status : Status
    , modules : List Plugin
    , directory : String
    , updates : Int
    , comments : String
    , showJson : Bool
    , showData : Bool
    , version : String
    , ready : String
    }


defaultExperiment : Experiment
defaultExperiment =
    { status = New
    , modules = []
    , directory = "/tmp/place_tmp"
    , updates = 1
    , comments = ""
    , showJson = False
    , showData = False
    , version = "0.0.0"
    , ready = "PLACE loading"
    }


type ExperimentMsg
    = ChangeDirectory String
    | ChangeUpdates String
    | ChangeShowJson Bool
    | ChangeShowData Bool
    | ChangeComments String
    | PostResponse (Result Http.Error (Dict String String))
    | UpdateModules Json.Encode.Value
    | StartExperiment
    | GetStatus ()
    | StatusResponse (Result Http.Error (Dict String String))
