workspace "E-commerce Platform" "Provides a platform for online shopping." {

    model {
        customer = person "Customer" "A user who shops online using the platform."

        ecommerce = softwareSystem "E-commerce Platform" "Provides a platform for online shopping." "React, Node.js, Java Spring Boot, Python FastAPI, Go, .NET Core, PostgreSQL, MongoDB, Redis, Apache Kafka" {
            frontend = container "Frontend System" "Web and mobile user interface for customers." "React"
            apiGateway = container "API Gateway" "Routes API requests to backend services." "Node.js"
            userService = container "User Service" "Manages user accounts, authentication, and profiles." "Java Spring Boot"
            productService = container "Product Service" "Manages product catalog and inventory." "Python FastAPI"
            orderService = container "Order Service" "Handles order creation, updates, and tracking." "Go"
            paymentService = container "Payment Service" "Handles payment processing and integration with payment gateways." ".NET Core"
            notificationService = container "Notification Service" "Sends notifications via email and SMS." "Node.js"
            databaseLayer = container "Database Layer" "Stores persistent data for users, products, orders, etc." "PostgreSQL, MongoDB, Redis"
            messageQueue = container "Message Queue" "Handles asynchronous communication between services." "Apache Kafka"

            customer -> frontend "Browses and shops online using"
            frontend -> apiGateway "Sends requests" "HTTP"
            apiGateway -> userService "Routes requests" "HTTP"
            apiGateway -> productService "Routes requests" "HTTP"
            apiGateway -> orderService "Routes requests" "HTTP"
            apiGateway -> paymentService "Routes requests" "HTTP"
            apiGateway -> notificationService "Routes requests" "HTTP"
            userService -> databaseLayer "Read/Write data" "SQL, NoSQL"
            productService -> databaseLayer "Read/Write data" "SQL, NoSQL"
            orderService -> databaseLayer "Read/Write data" "SQL, NoSQL"
            paymentService -> databaseLayer "Read/Write data" "SQL, NoSQL"
            notificationService -> databaseLayer "Read/Write data" "SQL, NoSQL"
            userService -> messageQueue "Send/Receive messages" "Apache Kafka"
            productService -> messageQueue "Send/Receive messages" "Apache Kafka"
            orderService -> messageQueue "Send/Receive messages" "Apache Kafka"
            paymentService -> messageQueue "Send/Receive messages" "Apache Kafka"
            notificationService -> messageQueue "Send/Receive messages" "Apache Kafka"
        }

        paymentGateways = softwareSystem "Payment Gateways" "Processes payments." "Stripe, PayPal" {
            tags "external_system","payment"
        }
        emailService = softwareSystem "Email Service" "Sends emails." "SendGrid" {
            tags "external_system","email"
        }
        smsService = softwareSystem "SMS Service" "Sends SMS." "Twilio" {
            tags "external_system","sms"
        }
        productSearchApi = softwareSystem "Product Search and Recommendations API" "Provides product search and recommendations." "Third-party API" {
            tags "external_system","search","recommendations"
        }

        paymentService -> paymentGateways "Processes payments" "API"
        notificationService -> emailService "Sends emails" "API"
        notificationService -> smsService "Sends SMS" "API"
        productService -> productSearchApi "Fetches product search and recommendations" "API"
    }

    views {
        systemContext ecommerce "SystemContext" {
            include *
            autoLayout
        }

        container ecommerce "Containers" {
            include *
            autoLayout
        }
    }
}