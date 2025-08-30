workspace {
    model {
        system = softwareSystem "System" "The system described in the specification"

        user_interface = component "User Interface" "The interface where users enter their questions and information about the system."
        parser = component "Parser" "Processes and interprets the user input to extract relevant information."
        summarizer = component "Summarizer" "Summarizes the parsed information into a concise format."
        dsl_generator = component "DSL Generator" "Generates a Domain-Specific Language (DSL) based on the summarized information."

        user_interface -> parser "User inputs are sent from the User Interface to the Parser for processing."
        parser -> summarizer "The parsed information is forwarded from the Parser to the Summarizer for summarization."
        summarizer -> dsl_generator "The summarized information is passed from the Summarizer to the DSL Generator to create the DSL."
    }
    views {
        component system "System_Component" "Component Diagram" {
            include *
        }
    }
}