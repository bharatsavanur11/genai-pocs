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
