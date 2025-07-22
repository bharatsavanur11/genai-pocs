workspace {
    model {
        system = softwareSystem "System" "The system described in the specification"

        user_interface = component "User Interface" "The front-end component that users interact with to access the web application."
        backend_service = component "Backend Service" "The server-side component that processes requests from the User Interface and handles business logic."
        database = component "Database" "The storage component that holds the application's data and is accessed by the Backend Service."

        user_interface -> backend_service "The User Interface sends requests to the Backend Service to retrieve or manipulate data."
        backend_service -> database "The Backend Service queries and updates the Database to fulfill requests from the User Interface."
    }
    views {
        component system "System_Component" "Component Diagram" {
            include *
        }
    }
}