# Copyright 2023 Fe-Ti aka T.Kravchenko

# Scenery sections
Start_state     = "start_state"
Hint_template   = "hint_template"
States          = "states"
Phrases         = "phrases"
Errors          = "errors"
Infos           = "infos"
Commands        = "commands"

# Commands
Info    = "info"
Reset   = "reset"
Cancel  = "cancel"
Repeat  = "repeat"

# Keywords in state
Type        = "Type"
Error       = "Error"
Info        = "Info" # help message
Phrase      = "Phrase" # short help. sort of  tl:dr
Next        = "Next"
Set         = "Set" # Set variables {"name" : value}
Input       = "Input"
Functions   = "Functions" # A list of functions to run, e.g.:
                        # Functions: [["create","not user.approve"], reset_user]
                        # The first will run only when expression is true
                        # and if the function is allowed to be called.
                        # Note: the expression is currently evaluated by eval()
                        # Note 2: allowed functions are defined in config

Properties  = "Properties"  # Determines how the state is interpreted.
                            # Is an array (list) of strings, e.g.:
                            # Properties: [Lexeme_preserving, Phrase_formatting]

# Property list
Phrase_formatting   = "Phrase_formatting" # If present, then phrase is formatted like f"..."
Say_anyway          = "Say_anyway" # If present, then bot sends phrase in any case
Lexeme_preserving   = "Lexeme_preserving" # If present, then lexeme is preserved for the next state
Input_checking      = "Input_checking" # If present in Get, then lexeme is checked against Storage[Check_list] (if it exists or not empty)

# Types
Say = 0 # Just say and go further
Get = 1 # Get the value of something
Ask = 2 # Ask and choose next

#
Settings        = "Settings"
Key             = "Key"
Show_hints      = "Show_hints"
Notify          = "Notify"
# ~ Reset_if_error  = "Reset_if_error"

Data        = "Data" # JSON data
Parameters  = "Parameters" # HTTP params

Storage     = "Storage"
State_stack = "State_stack"
JMP_state   = "JMP_state"
Context     = "Context" # Context, e.g. project, issue... used as type of object
Check_list  = "Check_list"

# Contexts
Global  = "Global"
Issue   = "Issue"
Project = "Project"

# Misc Constants
Default         = "Default"
Notification    = "Notification"

Success         = "Success"
