module ExperimentResult exposing (ExperimentResult(..), decode)

import Experiment exposing (Experiment)
import Json.Decode as D
import Progress exposing (Progress)


{-| The result in the experiment folder after the experiment has completed.
-}
type ExperimentResult
    = Completed Progress
    | Aborted Experiment
    | Empty String


decode : D.Decoder ExperimentResult
decode =
    D.field "result" D.string
        |> D.andThen
            (\result ->
                case result of
                    "completed" ->
                        D.field "progress" Progress.decode
                            |> D.andThen
                                (\progress ->
                                    D.succeed <| Completed progress
                                )

                    "aborted" ->
                        D.field "experiment" Experiment.decode
                            |> D.andThen
                                (\experiment ->
                                    D.succeed <| Aborted experiment
                                )

                    otherwise ->
                        D.field "location" D.string
                            |> D.andThen
                                (\location ->
                                    D.succeed <| Empty location
                                )
            )
