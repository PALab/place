module Experiment exposing (ExperimentMsg(..), defaultExperiment, update)

import Process
import Task
import Time
import Http
import Dict exposing (Dict)
import Json.Encode
import Json.Decode
import Experiment.Model exposing (Experiment, Status(..))
import Experiment.Plugin exposing (Plugin)


defaultExperiment : Experiment
defaultExperiment =
    { status = New
    , plugins = []
    , updates = 1
    , comments = ""
    , version = Experiment.Model.Version 0 0 0
    , ready = "Loading"
    }


type ExperimentMsg
    = ChangeUpdates String
    | ChangeComments String
    | PostResponse (Result Http.Error (Dict String String))
    | UpdatePlugins Json.Encode.Value
    | StartExperiment
    | GetStatus ()
    | StatusResponse (Result Http.Error (Dict String String))


update : ExperimentMsg -> Experiment -> ( Experiment, Cmd ExperimentMsg )
update msg experiment =
    case msg of
        ChangeUpdates newValue ->
            ( { experiment | updates = Result.withDefault 1 <| String.toInt newValue }, Cmd.none )

        ChangeComments newValue ->
            ( { experiment | comments = newValue }, Cmd.none )

        UpdatePlugins jsonValue ->
            case Json.Decode.decodeValue (Json.Decode.list Experiment.Plugin.decode) jsonValue of
                Ok newData ->
                    let
                        newState =
                            case List.head newData of
                                Nothing ->
                                    experiment

                                Just data ->
                                    { experiment
                                        | plugins =
                                            ((if data.className == "None" then
                                                emptyPlugins
                                              else
                                                newData
                                             )
                                                ++ List.filter
                                                    (.module_name >> ((/=) data.module_name))
                                                    experiment.plugins
                                            )
                                    }
                    in
                        ( newState, Cmd.none )

                Err err ->
                    ( { experiment | status = Experiment.Model.Error }, Cmd.none )

        PostResponse (Ok dict) ->
            case Dict.get "status" dict of
                Just string ->
                    update (GetStatus ()) { experiment | comments = string }

                Nothing ->
                    ( { experiment | comments = "no \"status\" key in dictionary" }, Cmd.none )

        PostResponse (Err err) ->
            ( { experiment | comments = toString err }, Cmd.none )

        StartExperiment ->
            let
                body =
                    Http.jsonBody (Experiment.Model.encode experiment)
            in
                ( experiment
                , Http.send PostResponse <|
                    Http.post "submit/" body <|
                        Json.Decode.dict Json.Decode.string
                )

        GetStatus () ->
            ( experiment
            , Http.send StatusResponse <|
                Http.get "status/" <|
                    Json.Decode.dict Json.Decode.string
            )

        StatusResponse (Ok dict) ->
            case Dict.get "status" dict of
                Just string ->
                    let
                        new_experiment =
                            { experiment | ready = string }
                    in
                        if new_experiment.ready == "Ready" then
                            ( new_experiment, Cmd.none )
                        else
                            ( new_experiment, Task.perform GetStatus (Process.sleep (500 * Time.millisecond)) )

                Nothing ->
                    ( { experiment | comments = "no \"status\" key in dictionary" }, Cmd.none )

        StatusResponse (Err err) ->
            ( { experiment | ready = toString err }, Cmd.none )


emptyPlugins : List Plugin
emptyPlugins =
    []
