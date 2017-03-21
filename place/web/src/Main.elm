module Main exposing (..)

import Html
import WebSocket
import PlaceDefaults exposing (..)
import PlaceView


{-| A webapp for interfacing with the included scan.py script. It is
still very much in development.
-}
main : Program Never Model Msg
main =
    Html.program
        { init = ( placeDefaults, Cmd.none )
        , view = PlaceView.view
        , update = update
        , subscriptions = subscriptions
        }


{-| This function calls the appropriate model changing
function based on the *Msg* received as input.

Reading the Elm code here can be complicated. As an
example, take the case:

    Changekey newValue ->
        ( { model | key = newValue }, Cmd.none )

This can be read as,

"Changekey, give the input `newValue`, returns the model, such that the
value `key' is reassigned to the value `newValue`. It also returns the
null command, `Cmd.none`."
-}
update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        Togglehelp ->
            ( { model | help = not model.help }, Cmd.none )

        Changekey newValue ->
            ( { model | key = newValue }, Cmd.none )

        Changen newValue ->
            ( { model | n = newValue }, Cmd.none )

        Changen2 newValue ->
            ( { model | n2 = newValue }, Cmd.none )

        Changescan newValue ->
            ( { model | scan = newValue }, Cmd.none )

        Changes1 newValue ->
            ( { model | s1 = newValue }, Cmd.none )

        Changes2 newValue ->
            ( { model | s2 = newValue }, Cmd.none )

        Changedm newValue ->
            ( { model | dm = newValue }, Cmd.none )

        Changesr newValue ->
            ( { model | sr = newValue }, Cmd.none )

        Changetm newValue ->
            ( { model | tm = newValue }, Cmd.none )

        Changech newValue ->
            ( { model | ch = newValue }, Cmd.none )

        Changech2 newValue ->
            ( { model | ch2 = newValue }, Cmd.none )

        Changeav newValue ->
            ( { model | av = newValue }, Cmd.none )

        Changewt newValue ->
            ( { model | wt = newValue }, Cmd.none )

        Changetl newValue ->
            ( { model | tl = newValue }, Cmd.none )

        Changetr newValue ->
            ( { model | tr = newValue }, Cmd.none )

        Changecr newValue ->
            ( { model | cr = newValue }, Cmd.none )

        Changecr2 newValue ->
            ( { model | cr2 = newValue }, Cmd.none )

        Changecp newValue ->
            ( { model | cp = newValue }, Cmd.none )

        Changecp2 newValue ->
            ( { model | cp2 = newValue }, Cmd.none )

        Changeohm newValue ->
            ( { model | ohm = newValue }, Cmd.none )

        Changeohm2 newValue ->
            ( { model | ohm2 = newValue }, Cmd.none )

        Changei1 newValue ->
            ( { model | i1 = newValue }, Cmd.none )

        Changed1 newValue ->
            ( { model | d1 = newValue }, Cmd.none )

        Changef1 newValue ->
            ( { model | f1 = newValue }, Cmd.none )

        Changei2 newValue ->
            ( { model | i2 = newValue }, Cmd.none )

        Changed2 newValue ->
            ( { model | d2 = newValue }, Cmd.none )

        Changef2 newValue ->
            ( { model | f2 = newValue }, Cmd.none )

        Changerv newValue ->
            ( { model | rv = newValue }, Cmd.none )

        Changerv2 newValue ->
            ( { model | rv2 = newValue }, Cmd.none )

        Changedd newValue ->
            ( { model | dd = newValue }, Cmd.none )

        Changerg newValue ->
            ( { model | rg = newValue }, Cmd.none )

        Changevch newValue ->
            ( { model | vch = newValue }, Cmd.none )

        Changesl newValue ->
            ( { model | sl = newValue }, Cmd.none )

        Changepp newValue ->
            ( { model | pp = newValue }, Cmd.none )

        Changebp newValue ->
            ( { model | bp = newValue }, Cmd.none )

        Changeso newValue ->
            ( { model | so = newValue }, Cmd.none )

        Changeen newValue ->
            ( { model | en = newValue }, Cmd.none )

        Changelm newValue ->
            ( { model | lm = newValue }, Cmd.none )

        Changerr newValue ->
            ( { model | rr = newValue }, Cmd.none )

        Changepl newValue ->
            ( { model | pl = newValue }, Cmd.none )

        Changemap newValue ->
            ( { model | map = newValue }, Cmd.none )

        Changecomments newValue ->
            ( { model | comments = newValue }, Cmd.none )

        Changeosci newValue ->
            ( { model
                | osci = newValue
                , ch = placeDefaults.ch
                , ch2 = placeDefaults.ch2
                , cr = placeDefaults.cr
                , cr2 = placeDefaults.cr2
                , cp = placeDefaults.cp
                , cp2 = placeDefaults.cp2
                , ohm = placeDefaults.ohm
                , ohm2 = placeDefaults.ohm2
              }
            , Cmd.none
            )

        SetKey ->
            ( { model | keySet = True }, Cmd.none )

        Scan ->
            ( placeDefaults
            , WebSocket.send "ws://localhost:9130"
                (model.key ++ " " ++ PlaceView.makeCmd model)
            )

        Response str ->
            ( { model | response = str }, Cmd.none )



-- SUBSCRIPTIONS


subscriptions : Model -> Sub Msg
subscriptions model =
    WebSocket.keepAlive "ws://localhost:9130"
