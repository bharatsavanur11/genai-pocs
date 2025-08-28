```
workspace {

  model {
    user = person "User" "A user of the e-commerce platform"
    ecommerce = softwareSystem "E-commerce Platform" "Provides a platform for online shopping" {
      tags "React", "Node.js", "Java Spring Boot", "Python FastAPI", "Go", ".NET Core", "PostgreSQL", "MongoDB", "Redis", "Apache Kafka"
    }
    payment = softwareSystem "Payment Gateways" "Processes payments" {
      tags "Stripe", "PayPal"
    }
    email = softwareSystem "Email Service" "Sends emails" {
      tags "SendGrid"
    }
    sms = softwareSystem "SMS Service" "Sends SMS" {
      tags "Twilio"
    }
    search = softwareSystem "Product Search and Recommendations API" "Provides product search and recommendations" {
      tags "Third-party API"
    }

    user -> ecommerce "Uses"
    ecommerce -> payment "Processes payments"
    ecommerce -> email "Sends emails"
    ecommerce -> sms "Sends SMS"
    ecommerce -> search "Gets product recommendations"
  }

  views {
    systemContext ecommerce {
      include *
      autoLayout
    }

    styles {
      element "softwareSystem" {
        background #1168bd
        color #ffffff
      }
      element "person" {
        background #08427b
        color #ffffff
      }
      element "React", "Node.js", "Java Spring Boot", "Python FastAPI", "Go", ".NET Core", "PostgreSQL", "MongoDB", "Redis", "Apache Kafka", "Stripe", "PayPal", "SendGrid", "Twilio", "Third-party API" {
        color #6c757d
      }
    }
  }
}
```