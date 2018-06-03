module Place.State exposing (update)

import Time
import Process
import Task
import Http
import Json.Decode
import Place.Model exposing (Model, Msg(..), PlacePlugin)
import Place.Encode
import Place.Decode
import Place.View


update : Msg -> Model -> ( Model, Cmd Msg )
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
                    let
                        newState =
                            { modules = emptyPlugins
                            , directory = ""
                            , updates = 0
                            , comments = err
                            , plotData = Place.View.errorPlotView
                            , showJson = False
                            , showData = False
                            , version = "0.0.0"
                            , ready = "Error"
                            }
                    in
                        ( { newState | version = experiment.version }, Cmd.none )

        PostResponse (Ok string) ->
            update (GetStatus ()) { experiment | comments = string }

        PostResponse (Err err) ->
            ( { experiment | comments = toString err }, Cmd.none )

        StartExperiment ->
            ( experiment
            , Http.send PostResponse
                (Http.post "start/" (Http.jsonBody (Place.Encode.toJson experiment)) Json.Decode.string)
            )

        GetStatus () ->
            ( experiment, Http.send StatusResponse (Http.getString "status/") )

        StatusResponse (Ok string) ->
            let
                new_experiment =
                    { experiment | ready = string }
            in
                if string == "Ready" then
                    ( new_experiment, Cmd.none )
                else
                    ( new_experiment, Task.perform GetStatus (Process.sleep (500 * Time.millisecond)) )

        StatusResponse (Err err) ->
            ( { experiment | comments = toString err }, Cmd.none )


emptyPlugins : List PlacePlugin
emptyPlugins =
    []
