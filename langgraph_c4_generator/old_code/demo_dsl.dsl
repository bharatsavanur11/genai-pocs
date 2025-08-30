workspace {
    name "C4 Architecture Diagram"
    description "Generated from technical specification"

    model {
        web_server = component "Web Server" "Handles HTTP requests and serves web pages"
        database = component "Database" "Stores application data"

        web_server -> database "Queries and updates data"
    }

    views {
        component system "Components" "Component Diagram" {
            include *
        }
    }
}