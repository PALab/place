-- STEP 1:
-- set the module name to be the same as the file name,
-- but without the .elm extenstion


port module PLACETemplate exposing (main)

import Html exposing (Html)
import Html.Events
import Html.Attributes
import Json.Encode
import ModuleHelpers


-- STEP 2:
-- Fill in information for who wrote this module, who maintains it currently,
-- and a contact email address.


attributions : ModuleHelpers.Attributions
attributions =
    { authors = [ "Dr. A. Place" ]
    , maintainer = "Mo Places"
    , maintainerEmail = "moplaces@everywhere.com"
    }



-- STEP 3:
-- change placeModuleName to be the name that shows as the title
-- of your GUI box within the PLACE interface


placeModuleName =
    "PLACETemplate"



-- STEP 4:
-- change pythonModuleName to be the name of your Python module


pythonModuleName =
    "place_template"



-- STEP 5:
-- change pythonClassName to be the name of your Python class


pythonClassName =
    "PLACETemplate"



-- STEP 6:
-- set defaultPriority to be the default PLACE priority


defaultPriority =
    "10"



-- STEP 7:
-- Add variables needed from the user into this data structure.  Generally, you
-- will use Bool or String. Often you will need Int and Float values. These are
-- usually best kept as stings within the Elm code and converted to number
-- formats when the JSON is written.


type alias Model =
    { className : String
    , active : Bool
    , priority : String
    }



-- STEP 8:
-- For each variable you added, assign it a default value in the defaultModel.


defaultModel : Model
defaultModel =
    { className = "None"
    , active = False
    , priority = defaultPriority
    }



-- STEP 9:
-- Add a message to change each variable you added. If you aren't sure what to
-- name them, general PLACE convention is to prefix Toggle to variable name if
-- it is a boolean or prefix Change if it is one of the other types.
--
-- Note that all UI elements to manipulate Int, Float, and String variables
-- will return a String from the user, so even if you have a Float variable
-- named "mass", your message from the UI will be something like ChangeMass
-- String, because the UI will send a String based on the keyboard input from
-- the user.


type Msg
    = ToggleActive
    | SendJson
    | Close
    | ChangePriority String



-- STEP 10:
-- In this step, we will write what happens when the UI sends us a message.
-- This message is sent whenever the user changes something on the UI. So, each
-- time the user types a digit into an integer box, we want to make sure we
-- update the value in our model. This means that generally, we will handle
-- messages by simply updating the appropriate variable, depending on the
-- message received. Examples have been provided to get you started.


updateModel : Msg -> Model -> ( Model, Cmd Msg )
updateModel msg model =
    (case msg of
        ToggleActive ->
            toggleActive model

        SendJson ->
            sendJson model

        Close ->
            close

        -- -- EXAMPLE BOOL UPDATE
        -- TogglePlot ->
        --     newModel { model | plot = not model.plot }
        --
        -- -- EXAMPLE STRING, INT, FLOAT UPDATE
        -- ChangeNote newNote ->
        --     newModel { model | note = newNote }
        --
        -- ChangeSamples newSamples ->
        --     newModel { model | samples = newSamples }
        --
        -- ChangeStart newStart ->
        --     newModel { model | start = newStart }
        --
        ChangePriority newPriority ->
            changePriority newPriority model
    )



-- STEP 11:
-- Add interactive elements for each variable you added into the model.
--
-- You can add checkboxes to manipulate boolean values, integer input fields,
-- float input fields, and string input fields.  Additionally, there is a
-- dropdown menu element, to allow selection from a limited number of strings.
-- Put all these elements between the square brackets and separated by commas.
--
-- For most of these functions, you pass the text description of the element,
-- the variable to hold the result, and the message to manipulate the variable.
-- So if, for example, I needed the user to manipulate a float value to
-- describe the velocity, my interactive element might be described with this
-- code:
--
--     ModuleHelpers.floatField "Velocity" model.velocity ChangeVelocity
--
-- You can find these functions in the ModuleHelpers.elm file, or you can look
-- at other modules for examples.


userInteractionsView : Model -> List (Html Msg)
userInteractionsView model =
    [ ModuleHelpers.integerField "Priority" model.priority ChangePriority

    -- -- SAMPLE CHECKBOX
    -- , ModuleHelpers.checkbox "Plot" model.plot ChangePlot
    --
    -- -- SAMPLE INTEGER FIELD
    -- , ModuleHelpers.integerField "Number of samples" model.samples ChangeSamples
    --
    -- -- SAMPLE FLOAT FIELD
    -- , ModuleHelpers.floatField "Angle" model.angle ChangeAngle
    --
    -- -- SAMPLE STRING FIELD
    -- , ModuleHelpers.stringField "Comment" model.comment ChangeComment
    --
    -- -- SAMPLER DROPDOWN BOX
    -- , ModuleHelpers.dropDownBox "Shape" model.shape ChangeShape [("circle", "Circle"), ("zigzag", "Zig Zag")]
    --
    -- Note that in the dropdown box, you must also pass the choices. The
    -- first string in each tuple is the value saved into the variable and the
    -- second is the more descriptive string shown to the user on the web
    -- interface.
    ]



-- STEP 12:
-- Each time a user interaction is made, PLACE updates the JSON text that will
-- be sent to the PLACE backend when the experiment is started. In this step,
-- we will update the JSON. As with other steps, there is a different way to
-- handle each type of variable, so examples are provided.
--
-- As mentioned previously, it is during this step that our Int and Float
-- values will be converted from the String values used in the web interface.
-- In the event that the user tries to start an experiment with illegal values
-- in the number fields, the default value is used.
--
-- This step is important because this is where you will actually define how
-- your Python module will access the values selected by the user in the web
-- interface. So, for example, if you have a variable named "linearDistance" in
-- the Elm Model and you associate it with the String "linear_distance" in this
-- step, then in your Python code, you would be able to access the linear
-- distance selected by the user by accessing self._config['linear_distance'].


jsonValues : Model -> List ( String, Json.Encode.Value )
jsonValues model =
    [--
     -- -- STRING
     -- ( "sample_description", Json.Encode.string model.sampleDescription )
     --
     -- -- INT
     -- ( "averages"
     -- , Json.Encode.int
     --       (Result.withDefault defaultModel.averages
     --           (String.toInt model.averages)
     --       )
     -- )
     --
     -- -- FLOAT
     -- ( "temperature"
     -- , Json.Encode.float
     --       (Result.withDefault defaultModel.temp
     --           (String.toFloat model.temp)
     --       )
     -- )
     --
     -- -- BOOL
     -- ( "extraProcessing", Json.Encode.bool model.extraProcessing )
     --
     -- Note: separate each tuple with a comma
    ]



-- STEP 13 (optional):
-- If your PLACE module records data, it is expected to register it in the
-- PLACE user interface. This allows users to get an accurate representation of
-- the data layout using the "Show Data Layout" button in the webapp. This is
-- simply a list of strings describing the data. Elm will prefix each sting
-- with the python class name and a dash, so a string "time" might become
-- "PLACETemplate-time".


dataRegister : List String
dataRegister =
    -- example: ["time", "position", "temperature"]
    []



----------------------------------------------
-- THINGS YOU PROBABLY DON"T NEED TO CHANGE --
----------------------------------------------


port jsonData : Json.Encode.Value -> Cmd msg


port removeModule : String -> Cmd msg


main : Program Never Model Msg
main =
    Html.program
        { init = ( defaultModel, Cmd.none )
        , view = \model -> Html.div [] (viewModel model)
        , update = updateModel
        , subscriptions = \_ -> Sub.none
        }


newModel : Model -> ( Model, Cmd Msg )
newModel model =
    updateModel SendJson model


viewModel : Model -> List (Html Msg)
viewModel model =
    (ModuleHelpers.titleWithAttributions
        placeModuleName
        model.active
        ToggleActive
        Close
        attributions
    )
        ++ if model.active then
            userInteractionsView model
           else
            [ ModuleHelpers.empty ]


toggleActive : Model -> ( Model, Cmd Msg )
toggleActive model =
    if model.active then
        newModel
            { model
                | className = "None"
                , active = False
            }
    else
        newModel
            { model
                | className = pythonClassName
                , active = True
            }


close : ( Model, Cmd Msg )
close =
    let
        ( clearModel, clearModelCmd ) =
            newModel defaultModel
    in
        clearModel ! [ clearModelCmd, removeModule pythonModuleName ]


changePriority : String -> Model -> ( Model, Cmd Msg )
changePriority newPriority model =
    newModel { model | priority = newPriority }


sendJson : Model -> ( Model, Cmd Msg )
sendJson model =
    ( model
    , jsonData
        (Json.Encode.list
            [ Json.Encode.object
                [ ( "module_name", Json.Encode.string pythonModuleName )
                , ( "class_name", Json.Encode.string model.className )
                , ( "priority"
                  , Json.Encode.int
                        (ModuleHelpers.intDefault defaultModel.priority model.priority)
                  )
                , ( "data_register"
                  , Json.Encode.list
                        (List.map Json.Encode.string
                            (List.map (\s -> (pythonClassName ++ "-" ++ s)) dataRegister)
                        )
                  )
                , ( "config", Json.Encode.object (jsonValues model) )
                ]
            ]
        )
    )
