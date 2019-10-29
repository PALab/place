port module PolytecOFV5000 exposing (main)

import Html exposing (Html)
import Html.Attributes
import Html.Events
import Json.Decode as D
import Json.Decode.Pipeline exposing (optional, required)
import Json.Encode as E
import Metadata exposing (Metadata)
import Plugin exposing (Plugin)
import PluginHelpers exposing (anOption)


common : Metadata
common =
    { title = "Polytec OFV-5000"
    , authors = [ "Paul Freeman" ]
    , maintainer = "Paul Freeman"
    , email = "paul.freeman.cs@gmail.com"
    , url = "https://github.com/palab/place"
    , elm =
        { moduleName = "PolytecOFV5000"
        }
    , python =
        { moduleName = "polytec"
        , className = "OFV5000"
        }
    , defaultPriority = "50"
    }


type alias Model =
    { dd300 : Bool
    , dd900 : Bool
    , vd08 : Bool
    , vd09 : Bool
    , dd300range : String
    , dd900range : String
    , vd08range : String
    , vd09range : String
    , timeout : String
    , autofocus : String
    , areaMin : String
    , areaMax : String
    , autofocusEverytime : Bool
    , plot : Bool
    }


dd300rangeDefault : String
dd300rangeDefault =
    "50nm/V"


dd900rangeDefault : String
dd900rangeDefault =
    "5mm/s/V"


vd08rangeDefault : String
vd08rangeDefault =
    "5mm/s/V"


vd09rangeDefault : String
vd09rangeDefault =
    "5mm/s/V"


default : Model
default =
    { dd300 = False
    , dd900 = False
    , vd08 = False
    , vd09 = False
    , dd300range = dd300rangeDefault
    , dd900range = dd900rangeDefault
    , vd08range = vd08rangeDefault
    , vd09range = vd09rangeDefault
    , timeout = "30.0"
    , autofocus = "none"
    , areaMin = "0"
    , areaMax = "3300"
    , autofocusEverytime = False
    , plot = False
    }


type Msg
    = ToggleDD300
    | ToggleDD900
    | ToggleVD08
    | ToggleVD09
    | ChangeDD900Range String
    | ChangeVD08Range String
    | ChangeVD09Range String
    | ChangeTimeout String
    | ChangeAutofocus String
    | ChangeAreaMin String
    | ChangeAreaMax String
    | ToggleEverytime
    | ChangePlot


update : Msg -> Model -> ( Model, Cmd Msg )
update msg vib =
    case msg of
        ToggleDD300 ->
            ( { vib | dd300 = not vib.dd300, dd300range = dd300rangeDefault }, Cmd.none )

        ToggleDD900 ->
            ( { vib | dd900 = not vib.dd900, dd900range = dd900rangeDefault }, Cmd.none )

        ToggleVD08 ->
            ( { vib | vd08 = not vib.vd08, vd08range = vd08rangeDefault }, Cmd.none )

        ToggleVD09 ->
            ( { vib | vd09 = not vib.vd09, vd09range = vd09rangeDefault }, Cmd.none )

        ChangeDD900Range newValue ->
            ( { vib | dd900range = newValue }, Cmd.none )

        ChangeVD08Range newValue ->
            ( { vib | vd08range = newValue }, Cmd.none )

        ChangeVD09Range newValue ->
            ( { vib | vd09range = newValue }, Cmd.none )

        ChangeTimeout newValue ->
            ( { vib | timeout = newValue }, Cmd.none )

        ChangeAutofocus newValue ->
            if newValue == "none" then
                ( { vib
                    | autofocus = "none"
                    , areaMin = default.areaMin
                    , areaMax = default.areaMax
                    , autofocusEverytime = False
                  }
                , Cmd.none
                )

            else if newValue /= "custom" then
                ( { vib
                    | autofocus = newValue
                    , areaMin = default.areaMin
                    , areaMax = default.areaMax
                  }
                , Cmd.none
                )

            else
                ( { vib | autofocus = newValue }, Cmd.none )

        ChangeAreaMin newValue ->
            ( { vib | areaMin = newValue }, Cmd.none )

        ChangeAreaMax newValue ->
            ( { vib | areaMax = newValue }, Cmd.none )

        ToggleEverytime ->
            ( { vib | autofocusEverytime = not vib.autofocusEverytime }, Cmd.none )

        ChangePlot ->
            ( { vib | plot = not vib.plot }, Cmd.none )



--------------------
-- MAIN HTML VIEW --
--------------------


userInteractionsView : Model -> List (Html Msg)
userInteractionsView vib =
    selectDecoders vib
        :: (if vib.dd300 || vib.dd900 || vib.vd08 || vib.vd09 then
                inputRange vib
                    ++ selectAutofocus vib
                    ++ [ PluginHelpers.checkbox "Plot" vib.plot ChangePlot ]

            else
                [ Html.text "" ]
           )


selectDecoders : Model -> Html Msg
selectDecoders model =
    Html.p []
        [ Html.text "Decoders: "
        , PluginHelpers.checkbox "DD-300" model.dd300 ToggleDD300
        , PluginHelpers.checkbox "DD-900" model.dd900 ToggleDD900
        , PluginHelpers.checkbox "VD-08" model.vd08 ToggleVD08
        , PluginHelpers.checkbox "VD-09" model.vd09 ToggleVD09
        ]


inputRange : Model -> List (Html Msg)
inputRange vib =
    []
        ++ (if vib.dd300 then
                [ Html.p [] [ Html.text "DD-300 range: 50 nm/V" ]
                ]

            else
                [ Html.text "" ]
           )
        ++ (if vib.dd900 then
                [ Html.p []
                    [ Html.text "DD-900 range: "
                    , Html.select [ Html.Events.onInput ChangeDD900Range ]
                        [ anOption vib.dd900range "5mm/V" "5 mm/V"
                        , anOption vib.dd900range "2mm/V" "2 mm/V"
                        , anOption vib.dd900range "1mm/V" "1 mm/V"
                        , anOption vib.dd900range "500um/V" "500 um/V"
                        , anOption vib.dd900range "200um/V" "200 um/V"
                        , anOption vib.dd900range "100um/V" "100 um/V"
                        , anOption vib.dd900range "50um/V" "50 um/V"
                        , anOption vib.dd900range "20um/V" "20 um/V"
                        , anOption vib.dd900range "10um/V" "10 um/V"
                        , anOption vib.dd900range "5um/V" "5 um/V"
                        , anOption vib.dd900range "2um/V" "2 um/V"
                        , anOption vib.dd900range "1um/V" "1 um/V"
                        , anOption vib.dd900range "500nm/V" "500 nm/V"
                        , anOption vib.dd900range "200nm/V" "200 nm/V"
                        , anOption vib.dd900range "100nm/V" "100 nm/V"
                        , anOption vib.dd900range "50nm/V" "50 nm/V"
                        ]
                    ]
                ]

            else
                []
           )
        ++ (if vib.vd08 then
                [ Html.p []
                    [ Html.text "VD-08 range: "
                    , Html.select [ Html.Events.onInput ChangeVD08Range ]
                        [ anOption vib.vd08range "50mm/s/V" "50 mm/s/V"
                        , anOption vib.vd08range "20mm/s/V" "20 mm/s/V"
                        , anOption vib.vd08range "10mm/s/V" "10 mm/s/V"
                        , anOption vib.vd08range "5mm/s/V" "5 mm/s/V"
                        , anOption vib.vd08range "2mm/s/V" "2 mm/s/V"
                        , anOption vib.vd08range "1mm/s/V" "1 mm/s/V"
                        , anOption vib.vd08range "0.5mm/s/V" "0.5 mm/s/V"
                        , anOption vib.vd08range "0.2mm/s/V" "0.2 mm/s/V"
                        ]
                    ]
                ]

            else
                []
           )
        ++ (if vib.vd09 then
                [ Html.p []
                    [ Html.text "VD-09 range: "
                    , Html.select [ Html.Events.onInput ChangeVD09Range ]
                        [ anOption vib.vd09range "1m/s/V" "1 m/s/V"
                        , anOption vib.vd09range "1m/s/V LP" "1 m/s/V LP"
                        , anOption vib.vd09range "500mm/s/V" "500 mm/s/V"
                        , anOption vib.vd09range "500mm/s/V LP" "500 mm/s/V LP"
                        , anOption vib.vd09range "200mm/s/V" "200 mm/s/V"
                        , anOption vib.vd09range "200mm/s/V LP" "200 mm/s/V LP"
                        , anOption vib.vd09range "100mm/s/V" "100 mm/s/V"
                        , anOption vib.vd09range "100mm/s/V LP" "100 mm/s/V LP"
                        , anOption vib.vd09range "50mm/s/V" "50 mm/s/V"
                        , anOption vib.vd09range "50mm/s/V LP" "50 mm/s/V LP"
                        , anOption vib.vd09range "20mm/s/V" "20 mm/s/V"
                        , anOption vib.vd09range "20mm/s/V LP" "20 mm/s/V LP"
                        , anOption vib.vd09range "10mm/s/V" "10 mm/s/V"
                        , anOption vib.vd09range "5mm/s/V" "5 mm/s/V"
                        ]
                    ]
                ]

            else
                []
           )


selectAutofocus : Model -> List (Html Msg)
selectAutofocus vib =
    [ PluginHelpers.dropDownBox
        "Autofocus"
        vib.autofocus
        ChangeAutofocus
        [ ( "none", "None" )
        , ( "small", "Small" )
        , ( "medium", "Medium" )
        , ( "full", "Full" )
        , ( "custom", "Custom" )
        ]
    ]
        ++ (if vib.autofocus == "custom" then
                [ PluginHelpers.integerField "Autofocus area minimum" vib.areaMin ChangeAreaMin
                , PluginHelpers.integerField "Autofocus area maximum" vib.areaMax ChangeAreaMax
                ]

            else
                []
           )
        ++ (if vib.autofocus /= "none" then
                [ PluginHelpers.checkbox "Autofocus every update" vib.autofocusEverytime ToggleEverytime
                , PluginHelpers.floatField "Autofocus timeout" vib.timeout ChangeTimeout
                ]

            else
                []
           )


encode : Model -> List ( String, E.Value )
encode vib =
    [ ( "dd_300", E.bool vib.dd300 )
    , ( "dd_900", E.bool vib.dd900 )
    , ( "vd_08", E.bool vib.vd08 )
    , ( "vd_09", E.bool vib.vd09 )
    , ( "dd_300_range", E.string vib.dd300range )
    , ( "dd_900_range", E.string vib.dd900range )
    , ( "vd_08_range", E.string vib.vd08range )
    , ( "vd_09_range", E.string vib.vd09range )
    , ( "autofocus", E.string vib.autofocus )
    ]
        ++ (if vib.autofocus == "custom" then
                [ ( "area_min"
                  , E.int <| PluginHelpers.intDefault default.areaMin vib.areaMin
                  )
                , ( "area_max"
                  , E.int <| PluginHelpers.intDefault default.areaMax vib.areaMax
                  )
                ]

            else
                []
           )
        ++ (if vib.autofocus /= "none" then
                [ ( "autofocus_everytime", E.bool vib.autofocusEverytime )
                , ( "timeout"
                  , E.float
                        (case String.toFloat vib.timeout of
                            Ok num ->
                                num

                            otherwise ->
                                -1.0
                        )
                  )
                ]

            else
                []
           )
        ++ [ ( "plot", E.bool vib.plot )
           ]


decode : D.Decoder Model
decode =
    D.succeed
        Model
        |> required "dd_300" D.bool
        |> required "dd_900" D.bool
        |> required "vd_08" D.bool
        |> required "vd_09" D.bool
        |> required "dd_300_range" D.string
        |> required "dd_900_range" D.string
        |> required "vd_08_range" D.string
        |> required "vd_09_range" D.string
        |> optional "timeout" (D.float |> D.andThen (D.succeed << toString)) default.timeout
        |> required "autofocus" D.string
        |> optional "area_min" (D.int |> D.andThen (D.succeed << toString)) default.areaMin
        |> optional "area_max" (D.int |> D.andThen (D.succeed << toString)) default.areaMax
        |> optional "autofocus_everytime" D.bool default.autofocusEverytime
        |> required "plot" D.bool


{-| Helper function to present an option in a drop-down selection box.
-}
anOption : String -> String -> String -> Html Msg
anOption str val disp =
    Html.option
        [ Html.Attributes.value val, Html.Attributes.selected (str == val) ]
        [ Html.text disp ]



----------------------------------------------
-- THINGS YOU PROBABLY DON"T NEED TO CHANGE --
----------------------------------------------


port config : E.Value -> Cmd msg


port removePlugin : String -> Cmd msg


port processProgress : (E.Value -> msg) -> Sub msg


main : Program Never PluginModel PluginMsg
main =
    Html.program
        { init = ( defaultModel, Cmd.none )
        , view = \model -> Html.div [] (viewModel model)
        , update = updatePlugin
        , subscriptions = always <| processProgress UpdateProgress
        }


type alias PluginModel =
    { active : Bool
    , priority : String
    , metadata : Metadata
    , config : Model
    , progress : E.Value
    }


defaultModel : PluginModel
defaultModel =
    { active = False
    , priority = common.defaultPriority
    , metadata = common
    , config = default
    , progress = E.null
    }


type PluginMsg
    = ToggleActive ------------ turn the plugin on and off on the webpage
    | ChangePriority String --- change the order of execution, relative to other plugins
    | ChangePlugin Msg -------- change one of the custom values in the plugin
    | SendToPlace ------------- sends the values in the model to PLACE
    | UpdateProgress E.Value -- update current progress of a running experiment
    | Close ------------------- close the plugin tab on the webpage


newModel : PluginModel -> ( PluginModel, Cmd PluginMsg )
newModel model =
    updatePlugin SendToPlace model


viewModel : PluginModel -> List (Html PluginMsg)
viewModel model =
    PluginHelpers.titleWithAttributions
        common.title
        model.active
        ToggleActive
        Close
        common.authors
        common.maintainer
        common.email
        ++ (if model.active then
                PluginHelpers.integerField "Priority" model.priority ChangePriority
                    :: List.map (Html.map ChangePlugin) (userInteractionsView model.config)
                    ++ [ PluginHelpers.displayAllProgress model.progress ]

            else
                [ Html.text "" ]
           )


updatePlugin : PluginMsg -> PluginModel -> ( PluginModel, Cmd PluginMsg )
updatePlugin msg model =
    case msg of
        ToggleActive ->
            if model.active then
                newModel { model | active = False }

            else
                newModel { model | active = True }

        ChangePriority newPriority ->
            newModel { model | priority = newPriority }

        ChangePlugin pluginMsg ->
            let
                config =
                    model.config

                ( newConfig, cmd ) =
                    update pluginMsg model.config

                newCmd =
                    Cmd.map ChangePlugin cmd

                ( updatedModel, updatedCmd ) =
                    newModel { model | config = newConfig }
            in
            ( updatedModel, Cmd.batch [ newCmd, updatedCmd ] )

        SendToPlace ->
            ( model
            , config <|
                E.object
                    [ ( model.metadata.elm.moduleName
                      , Plugin.encode
                            { active = model.active
                            , priority = PluginHelpers.intDefault model.metadata.defaultPriority model.priority
                            , metadata = model.metadata
                            , config = E.object (encode model.config)
                            , progress = E.null
                            }
                      )
                    ]
            )

        UpdateProgress value ->
            case D.decodeValue Plugin.decode value of
                Err err ->
                    ( { model | progress = E.string <| "Decode plugin error: " ++ err }, Cmd.none )

                Ok plugin ->
                    if plugin.active then
                        case D.decodeValue decode plugin.config of
                            Err err ->
                                ( { model | progress = E.string <| "Decode value error: " ++ err }, Cmd.none )

                            Ok config ->
                                newModel
                                    { active = plugin.active
                                    , priority = toString plugin.priority
                                    , metadata = plugin.metadata
                                    , config = config
                                    , progress = plugin.progress
                                    }

                    else
                        newModel defaultModel

        Close ->
            let
                ( clearModel, clearModelCmd ) =
                    newModel defaultModel
            in
            ( clearModel, Cmd.batch [ clearModelCmd, removePlugin model.metadata.elm.moduleName ] )
