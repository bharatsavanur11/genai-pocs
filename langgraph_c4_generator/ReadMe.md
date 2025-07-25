[Input Spec]
     ↓
[LLM Extractor Agent] --(partial model)--> [Validator Agent]
     ↓                                   ↙          ↘
[Missing Info Prompter] ←--- [User UI]   [Corrector Agent]
     ↓
[C4 JSON Builder]
     ↓
[Structurizr DSL Generator]
     ↓
[DSL Output Viewer]

################################

MVP 1.0
     Given a tech spec generate C4 diagram using agentic architecture
     Creation of agents and working towards it.

MVP 2.0
     MVP Tech Spec in best readable format that can be recommended
          An Excel with containers, components and relationships.
     Based on the tech spec description - how do we demo this?

MVP 3.0
     Now we have all of the above information how we can prompt the user to provide more information based on agents.


Use one of the existing projects as a sample 