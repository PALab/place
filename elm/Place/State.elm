module Place.State exposing (update)

import Time
import Process
import Task
import Http
import Json.Decode
import Place.Experiment exposing (Experiment, ExperimentMsg(..))
import Place.Plugin exposing (Plugin)
import Place.Encode
import Place.Decode
import Place.View


update : ExperimentMsg -> Experiment -> ( Experiment, Cmd ExperimentMsg )
update msg experiment =
    case msg of
        ChangeDirectory newValue ->
            ( { experiment | directory = newValue }, Cmd.none )

        ChangeUpdates newValue ->
            ( { experiment | updates = Result.withDefault 1 <| String.toInt newValue }, Cmd.none )

        ChangeShowJson newValue ->
            ( { experiment | showJson = newValue }, Cmd.none )

        ChangeShowData newValue ->
            ( { experiment | showData = newValue }, Cmd.none )

        ChangeComments newValue ->
            ( { experiment | comments = newValue }, Cmd.none )

        UpdateModules jsonValue ->
            case Place.Decode.fromJson jsonValue of
                Ok newData ->
                    let
                        newState =
                            case List.head newData of
                                Nothing ->
                                    experiment

                                Just data ->
                                    { experiment
                                        | modules =
                                            ((if data.className == "None" then
                                                emptyPlugins
                                              else
                                                newData
                                             )
                                                ++ List.filter
                                                    (.module_name >> ((/=) data.module_name))
                                                    experiment.modules
                                            )
                                    }
                    in
                        ( newState, Cmd.none )

                Err err ->
                    ( { experiment | status = Place.Experiment.Error }, Cmd.none )

        PostResponse (Ok string) ->
            update (GetStatus ()) { experiment | comments = string }

        PostResponse (Err err) ->
            ( { experiment | comments = toString err }, Cmd.none )

        StartExperiment ->
            let
                body =
                    Http.jsonBody (Place.Encode.toJson experiment)
            in
                ( experiment
                , Http.send PostResponse <|
                    Http.post "submit/" body Json.Decode.string
                )

        GetStatus () ->
            ( experiment
            , Http.send StatusResponse <|
                Http.get "status/" Json.Decode.string
            )

        StatusResponse (Ok string) ->
            let
                new_experiment =
                    { experiment | ready = string }
            in
                if new_experiment.ready == "Ready" then
                    ( new_experiment, Cmd.none )
                else
                    ( new_experiment, Task.perform GetStatus (Process.sleep (500 * Time.millisecond)) )

        StatusResponse (Err err) ->
            ( { experiment | ready = toString err }, Cmd.none )


emptyPlugins : List Plugin
emptyPlugins =
    []
