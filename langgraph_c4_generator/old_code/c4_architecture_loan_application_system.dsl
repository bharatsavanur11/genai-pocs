workspace {
    model {
        system = softwareSystem "System" "The system described in the specification"

        loan_application_portal = component "Loan Application Portal" "A web interface where customers can submit loan applications."
        loan_processing_service = component "Loan Processing Service" "A backend service that validates loan applications submitted by users."
        postgresql_database = component "PostgreSQL Database" "A relational database used to store loan application data and related information."
        credit_bureau_api = component "Credit Bureau API" "An external API that provides credit scores for applicants."

        loan_application_portal -> loan_processing_service "The Loan Application Portal sends submitted applications to the Loan Processing Service for validation."
        loan_processing_service -> postgresql_database "The Loan Processing Service stores validated loan application data in the PostgreSQL Database."
        loan_processing_service -> credit_bureau_api "The Loan Processing Service fetches credit scores from the Credit Bureau API to validate applications."
    }
    views {
        component system "System_Component" "Component Diagram" {
            include *
        }
    }
}