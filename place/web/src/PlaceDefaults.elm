module PlaceDefaults exposing (..)

{-| This is used to initialize the HTML program. -}
placeInit : (Model, Cmd Msg)
placeInit = (placeDefaults, Cmd.none)

{-| The model, or state, of this webapp consists of the values
associated with the command-line arguments for the scan.py script.

*help* is the only boolean value. The rest are consisdered Strings,
although many are actually integer values. However, since command-line
arguments are always passed as strings, this is appropriate for now. At
some point, to assist in data validation, it may be appropriate to
change some of these values to other types.
-}
type alias Model =
  { help    : Bool
  , n       : String
  , n2      : String
  , scan    : String
  , s1      : String
  , s2      : String
  , dm      : String
  , sr      : String
  , tm      : String
  , ch      : String
  , ch2     : String
  , av      : String
  , wt      : String
  , tl      : String
  , tr      : String
  , cr      : String
  , cr2     : String
  , cp      : String
  , cp2     : String
  , ohm     : String
  , ohm2    : String
  , i1      : String
  , d1      : String
  , f1      : String
  , i2      : String
  , d2      : String
  , f2      : String
  , rv      : String
  , rv2     : String
  , dd      : String
  , rg      : String
  , vch     : String
  , sl      : String
  , pp      : String
  , bp      : String
  , so      : String
  , en      : String
  , lm      : String
  , rr      : String
  , pl      : String
  , map     : String
  , comments: String
  , response: String
  }

{-| A Msg is a union type of all the possible functions which change the
PLACE model. -}
type Msg
  = Togglehelp
    | Changen        String
    | Changen2       String
    | Changescan     String
    | Changes1       String
    | Changes2       String
    | Changedm       String
    | Changesr       String
    | Changetm       String
    | Changech       String
    | Changech2      String
    | Changeav       String
    | Changewt       String
    | Changetl       String
    | Changetr       String
    | Changecr       String
    | Changecr2      String
    | Changecp       String
    | Changecp2      String
    | Changeohm      String
    | Changeohm2     String
    | Changei1       String
    | Changed1       String
    | Changef1       String
    | Changei2       String
    | Changed2       String
    | Changef2       String
    | Changerv       String
    | Changerv2      String
    | Changedd       String
    | Changerg       String
    | Changevch      String
    | Changesl       String
    | Changepp       String
    | Changebp       String
    | Changeso       String
    | Changeen       String
    | Changelm       String
    | Changerr       String
    | Changepl       String
    | Changemap      String
    | Changecomments String
    | Scan
    | Response String

{-| All default values should be placed here to provide one place for
changing them in the future. -}
helpDefault : Bool
helpDefault = False

scanDefault : String
scanDefault = "point"

s1Default : String
s1Default = "long"

s2Default : String
s2Default = "short"

dmDefault : String
dmDefault = "50"

srDefault : String
srDefault = "10M"

{-| The PLACE model is initialized with all the default values. -}
placeDefaults : Model
placeDefaults =
    { help    = helpDefault
    , n       = ""
    , n2      = ""
    , scan    = scanDefault
    , s1      = s1Default
    , s2      = s2Default
    , dm      = dmDefault
    , sr      = srDefault
    , tm      = ""
    , ch      = ""
    , ch2     = ""
    , av      = ""
    , wt      = ""
    , tl      = ""
    , tr      = ""
    , cr      = ""
    , cr2     = ""
    , cp      = ""
    , cp2     = ""
    , ohm     = ""
    , ohm2    = ""
    , i1      = ""
    , d1      = ""
    , f1      = ""
    , i2      = ""
    , d2      = ""
    , f2      = ""
    , rv      = ""
    , rv2     = ""
    , dd      = ""
    , rg      = ""
    , vch     = ""
    , sl      = ""
    , pp      = ""
    , bp      = ""
    , so      = ""
    , en      = ""
    , lm      = ""
    , rr      = ""
    , pl      = ""
    , map     = ""
    , comments= ""
    , response= ""
    }
