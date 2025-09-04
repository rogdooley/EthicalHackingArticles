
### **Article 1: Build Your Own SAML Identity and Relying Party**

- **Goal**: Set up a working SAML flow you control.
    
- **Deliverables**:
    
    - Dockerized IdP and SP (e.g., using [SAMLtest IdP](https://samltest.id) alternatives like [simplesamlphp](https://github.com/simplesamlphp/simplesamlphp)).
        
    - A basic browser-accessible SP endpoint that consumes SAML assertions.
        

### **Article 2: Parsing and Re-signing SAML Assertions**

- **Goal**: Use Python to read SAML, manipulate it, and re-sign it.
    
- **Tools**: `lxml`, `xmlsec`, `signxml`, or `pyXMLSecurity`.
    

### **Article 3: XML Signature Wrapping (XSW) Attacks**

- **Goal**: Write Python code to automate classic XSW variants.
    
- **Variants**: Enveloped, Enveloping, Detached Signature Injections.
    

### **Article 4: Token Replay and Assertion Forgery**

- **Goal**: Replay stolen assertions, modify them, and observe effects.
    
- **Bonus**: Use timestamp manipulation, missing audience, or bad NotBefore/NotOnOrAfter ranges.
    

### **Article 5: Detection and Mitigation**

- **Goal**: Show how to detect broken XML structures and invalid signatures.
    
- **Extras**: YARA rules, WAF patterns, Open Policy Agent rules.
    

### **Bonus Article: Browser Automation for Attack Flow**

- **Goal**: Automate logins, replay flows using Selenium or Playwright.
    

---

## **Your First Assignment: Part 1 — Minimal SAML Lab Setup**

### Goal:

Create a SAML lab with:

- One Identity Provider (IdP) you control
    
- One Service Provider (SP) that accepts logins
    

### Requirements:

- Use Docker Compose or manual setup
    
- IdP options:
    
    - [simplesamlphp](https://github.com/simplesamlphp/simplesamlphp)
        
    - [Keycloak](https://www.keycloak.org/) with SAML support
        
- SP:
    
    - Your own simple Flask app using [python3-saml](https://github.com/onelogin/python3-saml) or a known vulnerable SP
        
- Output:
    
    - Metadata files (IdP and SP)
        
    - A successful login flow (you can simulate user login with hardcoded credentials or default users)
        

### You should produce:

- Dockerfiles / docker-compose.yml (if used)
    
- SAML metadata for both SP and IdP
    
- Screenshot or description of successful SSO flow
    

Let me know if you want a lightweight setup (e.g., Flask + python3-saml + mock IdP) or something more real-world (e.g., Keycloak + real SP). Once you’re done, share your code and setup, and we’ll review together before moving to Part 2.

Would you like me to generate a basic scaffold for the Flask SP and IdP metadata files to speed up your start?