# Entity Onboarding System - Architecture Diagram

## Data Flow and Dependencies

```mermaid
graph TD
    %% Data Sources
    CL[Controlled Lists JSON<br/>- Source of Funds<br/>- Industry<br/>- Member Roles<br/>- Titles, Gender, Marital Status<br/>- Entity Types] 
    CN[Country List CSV<br/>220+ countries<br/>ISO codes]
    FS[Field Specifications JSON<br/>- Data types<br/>- Validation rules<br/>- UI controls<br/>- Dependencies]
    RS[Role Specifications JSON<br/>- Natural Person Roles<br/>- Entity Fields<br/>- Field mappings]
    ERR[Entity Role Rules JSON<br/>- Required roles per entity<br/>- Conditional roles<br/>- Min/max counts]
    DR[Document Requirements JSON<br/>- Entity documents<br/>- Role documents<br/>- Upload rules]
    
    %% Core Managers
    CLM[Controlled List Manager<br/>- Code/label resolution<br/>- Active item filtering<br/>- Sort ordering]
    FSM[Field Specification Manager<br/>- Validation engine<br/>- Dependency checking<br/>- Special validations]
    DRM[Document Requirements Manager<br/>- Upload validation<br/>- Schema generation<br/>- File format checking]
    
    %% Form System
    FB[Form Builder<br/>- Dynamic form generation<br/>- Component integration<br/>- UI rendering]
    VE[Validation Engine<br/>- Cross-field validation<br/>- Rule evaluation<br/>- Error reporting]
    
    %% Components
    AR[Authorised Representative<br/>Component]
    NP[Natural Persons<br/>Component]
    ADDR[Address<br/>Component]
    PHONE[Phone<br/>Component]
    
    %% Output
    AP[Application Payload<br/>+ Uploads Manifest]
    
    %% Data flow connections
    CL --> CLM
    CN --> CLM
    FS --> FSM
    RS --> FSM
    ERR --> FSM
    DR --> DRM
    
    CLM --> FB
    FSM --> FB
    FSM --> VE
    DRM --> VE
    
    FB --> AR
    FB --> NP
    FB --> ADDR
    FB --> PHONE
    
    AR --> VE
    NP --> VE
    ADDR --> VE
    PHONE --> VE
    
    VE --> AP
    
    %% Styling
    classDef dataSource fill:#e1f5fe
    classDef manager fill:#f3e5f5
    classDef component fill:#e8f5e8
    classDef output fill:#fff3e0
    
    class CL,CN,FS,RS,ERR,DR dataSource
    class CLM,FSM,DRM manager
    class FB,VE,AR,NP,ADDR,PHONE component
    class AP output
```

## Component Architecture

```mermaid
graph LR
    %% Entity Selection
    ET[Entity Type Selection] --> RR[Role Resolution]
    
    %% Role-based form generation
    RR --> AR[Authorised Representative<br/>REQUIRED for all]
    RR --> DIR[Directors<br/>Company]
    RR --> TRU[Trustees<br/>Trust]
    RR --> PAR[Partners<br/>Partnership]
    RR --> MEM[Members<br/>CC, Clubs, etc.]
    RR --> COM[Committee Members<br/>Societies, Groups]
    RR --> GOV[Governing Body<br/>Schools]
    RR --> LED[Leaders<br/>Churches]
    
    %% Common components
    AR --> ADDR1[Address Component]
    AR --> PHONE1[Phone Component]
    
    DIR --> ADDR2[Address Component]
    DIR --> PHONE2[Phone Component]
    
    TRU --> ADDR3[Address Component]
    TRU --> PHONE3[Phone Component]
    
    %% Entity details
    ET --> ED[Entity Details<br/>- Name, Registration<br/>- Source of Funds<br/>- Industry<br/>- Masters Office]
    
    %% Document requirements
    ET --> DOC[Document Requirements<br/>- Entity documents<br/>- Role-specific docs<br/>- Upload validation]
    
    %% Output
    AR --> OUT[Validation & Serialization]
    DIR --> OUT
    TRU --> OUT
    PAR --> OUT
    MEM --> OUT
    COM --> OUT
    GOV --> OUT
    LED --> OUT
    ED --> OUT
    DOC --> OUT
    
    OUT --> SUBMIT[Submission Payload]
    
    classDef entity fill:#e3f2fd
    classDef role fill:#f1f8e9
    classDef component fill:#fff8e1
    classDef output fill:#fce4ec
    
    class ET,RR,ED entity
    class AR,DIR,TRU,PAR,MEM,COM,GOV,LED role
    class ADDR1,ADDR2,ADDR3,PHONE1,PHONE2,PHONE3,DOC component
    class OUT,SUBMIT output
```

## Validation Flow

```mermaid
graph TD
    INPUT[User Input] --> FIELD[Field-level Validation]
    
    FIELD --> TYPE[Data Type Check]
    FIELD --> FORMAT[Format/Regex Check]
    FIELD --> LENGTH[Length Validation]
    FIELD --> RANGE[Value Range Check]
    
    TYPE --> SPECIAL[Special Validation]
    FORMAT --> SPECIAL
    LENGTH --> SPECIAL
    RANGE --> SPECIAL
    
    SPECIAL --> LUHN[Luhn Check<br/>SA ID Numbers]
    SPECIAL --> PHONE_VAL[Phone Format<br/>Country-specific]
    SPECIAL --> EMAIL[Email Format]
    SPECIAL --> POSTAL[Postal Code<br/>Country-specific]
    
    LUHN --> DEP[Dependency Validation]
    PHONE_VAL --> DEP
    EMAIL --> DEP
    POSTAL --> DEP
    
    DEP --> REQ[Required Field Check]
    DEP --> CROSS[Cross-field Logic]
    
    REQ --> ENTITY_TYPE{Entity Type}
    CROSS --> ENTITY_TYPE
    
    ENTITY_TYPE --> TRUST_MASTERS[Trust: Masters Office Required]
    ENTITY_TYPE --> REG_COUNTRY[Registration: Country Required if Number Provided]
    ENTITY_TYPE --> ID_DEPS[ID Type Dependencies]
    
    TRUST_MASTERS --> DOC_VAL[Document Validation]
    REG_COUNTRY --> DOC_VAL
    ID_DEPS --> DOC_VAL
    
    DOC_VAL --> ROLE_DOCS[Role-specific Documents]
    DOC_VAL --> ENTITY_DOCS[Entity Documents]
    DOC_VAL --> FORMAT_CHECK[File Format Check]
    DOC_VAL --> SIZE_CHECK[File Size Check]
    
    ROLE_DOCS --> FINAL[Final Validation]
    ENTITY_DOCS --> FINAL
    FORMAT_CHECK --> FINAL
    SIZE_CHECK --> FINAL
    
    FINAL --> PASS[✅ Validation Passed]
    FINAL --> FAIL[❌ Validation Failed<br/>Error Messages]
    
    classDef validation fill:#e8f5e8
    classDef check fill:#fff3e0
    classDef result fill:#ffebee
    
    class FIELD,TYPE,FORMAT,LENGTH,RANGE,SPECIAL,DEP,REQ,CROSS,DOC_VAL validation
    class LUHN,PHONE_VAL,EMAIL,POSTAL,TRUST_MASTERS,REG_COUNTRY,ID_DEPS,ROLE_DOCS,ENTITY_DOCS,FORMAT_CHECK,SIZE_CHECK check
    class PASS,FAIL result
```

## Key Benefits of New Architecture

### 🎯 **Structured Data Management**
- **Code/Label Separation**: UI displays labels, system stores codes
- **Versioned Controlled Lists**: Easy updates and rollback capability
- **Consistent Validation**: Single source of truth for all rules

### 🔧 **Enhanced Maintainability**
- **Declarative Specifications**: JSON-driven configuration
- **Role-based Architecture**: Reusable role definitions
- **Modular Validation**: Independent validation modules

### 🚀 **Scalability Features**
- **Dynamic Form Generation**: Forms built from specifications
- **Extensible Document Requirements**: Easy addition of new requirements
- **Cross-field Dependencies**: Complex business rule support

### 📊 **Data Integrity**
- **Structured Validation**: Multi-layer validation pipeline
- **Business Rule Enforcement**: Entity-specific logic
- **Document Compliance**: Upload validation and requirements checking

This architecture follows the semantic specification requirements and provides a robust foundation for entity onboarding with proper separation of concerns, maintainable code, and scalable design patterns.
