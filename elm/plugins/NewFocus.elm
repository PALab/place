port module NewFocus exposing (main)

import Html exposing (Html)
import Json.Decode as D
import Json.Decode.Pipeline exposing (hardcoded, optional, required)
import Json.Encode as E
import Metadata exposing (Metadata)
import Plugin exposing (Plugin)
import PluginHelpers


common : Metadata
common =
    { title = "New Focus picomotors"
    , authors = [ "Paul Freeman", "Jonathan Simpson" ]
    , maintainer = "Paul Freeman"
    , email = "paul.freeman.cs@gmail.com"
    , url = "https://github.com/palab/place"
    , elm =
        { moduleName = "NewFocus"
        }
    , python =
        { moduleName = "new_focus"
        , className = "Picomotor"
        }
    , defaultPriority = "20"
    }


type alias Model =
    { shape : String
    , xone : String
    , yone : String
    , xtwo : String
    , ytwo : String
    , radius : String
    , sectors : String
    , startingSector : String
    , plot : Bool
    , invertX : Bool
    , invertY : Bool
    , sleep : String
    , custom_filename : String
    }


default : Model
default =
    { shape = "none"
    , xone = "0"
    , yone = "0"
    , xtwo = "0"
    , ytwo = "0"
    , radius = "0"
    , sectors = "360"
    , startingSector = "0"
    , plot = False
    , invertX = True
    , invertY = True
    , sleep = "0.5"
    , custom_filename = ""
    }


type Msg
    = ChangeShape String
    | ChangeXOne String
    | ChangeYOne String
    | ChangeXTwo String
    | ChangeYTwo String
    | ChangeRadius String
    | ChangeSectors String
    | ChangeStartingSector String
    | ChangeSleep String
    | TogglePlot
    | ToggleInvertX
    | ToggleInvertY
    | ChangeCustomFilename String


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        ChangeShape newValue ->
            ( { model | shape = newValue }, Cmd.none )

        ChangeXOne newValue ->
            ( { model | xone = newValue }, Cmd.none )

        ChangeYOne newValue ->
            ( { model | yone = newValue }, Cmd.none )

        ChangeXTwo newValue ->
            ( { model | xtwo = newValue }, Cmd.none )

        ChangeYTwo newValue ->
            ( { model | ytwo = newValue }, Cmd.none )

        ChangeRadius newValue ->
            ( { model | radius = newValue }, Cmd.none )

        ChangeSectors newValue ->
            ( { model | sectors = newValue }, Cmd.none )

        ChangeStartingSector newValue ->
            ( { model | startingSector = newValue }, Cmd.none )

        ChangeSleep newValue ->
            ( { model | sleep = newValue }, Cmd.none )

        TogglePlot ->
            ( { model | plot = not model.plot }, Cmd.none )

        ToggleInvertX ->
            ( { model | invertX = not model.invertX }, Cmd.none )

        ToggleInvertY ->
            ( { model | invertY = not model.invertY }, Cmd.none )

        ChangeCustomFilename newValue ->
            ( { model | custom_filename = newValue }, Cmd.none )


userInteractionsView : Model -> List (Html Msg)
userInteractionsView model =
    PluginHelpers.dropDownBox "Shape"
        model.shape
        ChangeShape
        [ ( "none", "None" )
        , ( "point", "Point" )
        , ( "line", "Line" )
        , ( "circle", "Circle" )
        , ( "arc", "Arc" )
        , ( "custom", "Custom" )
        ]
        :: inputShape model
        ++ plotView model


inputShape : Model -> List (Html Msg)
inputShape model =
    case model.shape of
        "point" ->
            [ PluginHelpers.integerField "X1" model.xone ChangeXOne
            , PluginHelpers.integerField "Y1" model.yone ChangeYOne
            , PluginHelpers.floatField "Sleep" model.sleep ChangeSleep
            ]

        "line" ->
            [ PluginHelpers.integerField "X1" model.xone ChangeXOne
            , PluginHelpers.integerField "Y1" model.yone ChangeYOne
            , PluginHelpers.integerField "X2" model.xtwo ChangeXTwo
            , PluginHelpers.integerField "Y2" model.ytwo ChangeYTwo
            , PluginHelpers.floatField "Sleep" model.sleep ChangeSleep
            ]

        "circle" ->
            [ PluginHelpers.integerField "X1" model.xone ChangeXOne
            , PluginHelpers.integerField "Y1" model.yone ChangeYOne
            , PluginHelpers.integerField "Radius" model.radius ChangeRadius
            , PluginHelpers.floatField "Sleep" model.sleep ChangeSleep
            ]

        "arc" ->
            [ PluginHelpers.integerField "X1" model.xone ChangeXOne
            , PluginHelpers.integerField "Y1" model.yone ChangeYOne
            , PluginHelpers.integerField "Radius" model.radius ChangeRadius
            , PluginHelpers.integerField "Circle sectors" model.sectors ChangeSectors
            , PluginHelpers.integerField "Starting sector" model.startingSector ChangeStartingSector
            , PluginHelpers.floatField "Sleep" model.sleep ChangeSleep
            ]

        "custom" ->
            [ PluginHelpers.stringField "Full path to coordinate .txt file" model.custom_filename ChangeCustomFilename
            , PluginHelpers.floatField "Sleep" model.sleep ChangeSleep
            ]

        otherwise ->
            [ PluginHelpers.floatField "Sleep" model.sleep ChangeSleep ]


plotView : Model -> List (Html Msg)
plotView model =
    PluginHelpers.checkbox "Plot" model.plot TogglePlot
        :: (if model.plot then
                [ PluginHelpers.checkbox "Invert x-axis" model.invertX ToggleInvertX
                , PluginHelpers.checkbox "Invert y-axis" model.invertY ToggleInvertY
                ]

            else
                []
           )


encode : Model -> List ( String, E.Value )
encode model =
    [ ( "shape", E.string model.shape )
    , ( "x_one", E.int (PluginHelpers.intDefault default.xone model.xone) )
    , ( "y_one", E.int (PluginHelpers.intDefault default.yone model.yone) )
    , ( "x_two", E.int (PluginHelpers.intDefault default.xtwo model.xtwo) )
    , ( "y_two", E.int (PluginHelpers.intDefault default.ytwo model.ytwo) )
    , ( "radius", E.int (PluginHelpers.intDefault default.radius model.radius) )
    , ( "sectors", E.int (PluginHelpers.intDefault default.sectors model.sectors) )
    , ( "starting_sector", E.int (PluginHelpers.intDefault default.startingSector model.startingSector) )
    , ( "plot", E.bool model.plot )
    , ( "invert_x", E.bool model.invertX )
    , ( "invert_y", E.bool model.invertY )
    , ( "sleep_time", E.float (PluginHelpers.floatDefault default.sleep model.sleep) )
    , ( "custom_filename", E.string model.custom_filename )
    ]


decode : D.Decoder Model
decode =
    D.succeed
        Model
        |> required "shape" D.string
        |> required "x_one" (D.int |> D.andThen (D.succeed << toString))
        |> required "y_one" (D.int |> D.andThen (D.succeed << toString))
        |> required "x_two" (D.int |> D.andThen (D.succeed << toString))
        |> required "y_two" (D.int |> D.andThen (D.succeed << toString))
        |> required "radius" (D.int |> D.andThen (D.succeed << toString))
        |> required "sectors" (D.int |> D.andThen (D.succeed << toString))
        |> required "starting_sector" (D.int |> D.andThen (D.succeed << toString))
        |> required "plot" D.bool
        |> required "invert_x" D.bool
        |> required "invert_y" D.bool
        |> required "sleep_time" (D.float |> D.andThen (D.succeed << toString))
        |> required "custom_filename" D.string



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
                            , metadata = common
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
                                    , metadata = common
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
