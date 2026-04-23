# Kata Action Builder Skill

Expert skill for building bot actions in Kata Platform YAML flows - defining text responses, API calls, method invocations, and interactive messages.

## When to Use This Skill

Use this skill when you need to:
- Define text responses and templates
- Make API calls to external services
- Execute custom ES5 methods
- Create WhatsApp interactive messages (buttons, lists, quick replies)
- Send multi-channel messages
- Schedule timed actions
- Map and transform data from API responses
- Build conditional action execution

## Action Fundamentals

Actions are the bot's outputs - what happens when a state is entered. They can send messages, call APIs, execute methods, or trigger schedulers.

### Action Structure

```yaml
states:
  stateName:
    action:
      - name: actionName
        type: text               # text, template, api, method
        condition: 'true'        # Optional condition
        options:
          # Action-specific configuration
```

### Action Types

1. **Text** - Simple text messages
2. **Template** - Structured messages with buttons/quick replies
3. **API** - HTTP requests to external services
4. **Method** - Execute ES5 JavaScript functions

## Usage Patterns

### Pattern 1: Simple Text Action

Basic text response:

```yaml
actions:
  welcomeText:
    type: text
    options:
      text: "Hello! Welcome to our support bot."

states:
  welcome:
    action:
      - name: welcomeText
```

**When to use:**
- Simple, static messages
- Confirmations and acknowledgments
- Error messages

### Pattern 2: Dynamic Text with Variables

Text with context/data interpolation:

```yaml
actions:
  greetUser:
    type: text
    options:
      text: "Hi $(context.userName)! Your account balance is Rp $(data.balance)."

  showTicket:
    type: text
    options:
      text: |
        Ticket Created Successfully!

        Ticket Number: $(data.ticketNumber)
        Status: $(data.ticketStatus)
        Priority: $(data.priority)

        We'll contact you within 24 hours.
```

**Variable Syntax:**
- `$(context.field)` - From conversation context
- `$(data.field)` - From data scope
- `$(metadata.field)` - From system metadata
- `$(payload.field)` - From intent payload

### Pattern 3: WhatsApp Button Template

Interactive buttons (max 3 buttons):

```yaml
actions:
  menuButtons:
    type: template
    options:
      header: "Main Menu"
      body: "Please select an option:"
      buttons:
        - type: postback
          label: "Check Billing"
          payload:
            postback: "checkBilling"
            action: "billing"
        - type: postback
          label: "Report Issue"
          payload:
            postback: "reportIssue"
            action: "issue"
        - type: postback
          label: "Contact Support"
          payload:
            postback: "contactSupport"
            action: "support"
```

**Button Response:**
When clicked, creates intent with `payload.postback` and `payload.action`.

### Pattern 4: WhatsApp List Template

List selection (up to 10 items per section):

```yaml
actions:
  paymentMethodList:
    type: template
    options:
      header: "Select Payment Method"
      body: "Choose your preferred payment option:"
      button: "View Options"
      list:
        sections:
          - title: "E-Wallet"
            rows:
              - title: "OVO"
                description: "Pay with OVO"
                value:
                  postback: "selectPayment"
                  method: "ovo"
              - title: "GoPay"
                description: "Pay with GoPay"
                value:
                  postback: "selectPayment"
                  method: "gopay"
          - title: "Bank Transfer"
            rows:
              - title: "BCA"
                description: "BCA Virtual Account"
                value:
                  postback: "selectPayment"
                  method: "bca"
```

**List Response:**
When selected, creates intent with `payload` containing the `value` object.

### Pattern 5: Quick Reply

Quick reply buttons (inline):

```yaml
actions:
  confirmAction:
    type: template
    options:
      text: "Do you want to proceed with this action?"
      quickReplies:
        - type: postback
          label: "Yes"
          payload:
            postback: "confirm"
            value: "yes"
        - type: postback
          label: "No"
          payload:
            postback: "confirm"
            value: "no"
```

### Pattern 6: API Action

Call external HTTP API:

```yaml
actions:
  getBillingInfo:
    type: api
    options:
      method: GET
      uri: https://api.example.com/billing/$(context.customerId)
      headers:
        Authorization: "Bearer $(config.apiToken)"
        Content-Type: application/json
      mapping:
        # Map API response to data scope
        data:
          totalBill: $(result.response.body.total)
          dueDate: $(result.response.body.due_date)
          status: $(result.response.body.status)

  createTicket:
    type: api
    options:
      method: POST
      uri: https://api.example.com/tickets
      headers:
        Authorization: "Bearer $(config.apiToken)"
        Content-Type: application/json
      body:
        customer_id: $(context.customerId)
        issue_type: $(data.issueType)
        description: $(data.issueDescription)
        priority: "high"
      mapping:
        data:
          ticketNumber: $(result.response.body.ticket_number)
          ticketStatus: $(result.response.body.status)
```

**API Response Mapping:**
- `$(result.response.status)` - HTTP status code
- `$(result.response.body.field)` - Response body field
- `$(result.response.headers.field)` - Response header

### Pattern 7: Method Action

Execute custom ES5 method:

```yaml
methods:
  validatePhoneNumber:
    code: |
      function validatePhoneNumber(msg, ctx, dat, opts, cfg, result) {
        var phone = ctx.phoneNumber;
        var isValid = /^(08|628)[0-9]{8,11}$/.test(phone);

        return {
          command: 'updateContext',
          payload: {
            phoneValid: isValid,
            phoneFormatted: phone.replace(/^08/, '628')
          }
        };
      }

actions:
  validatePhone:
    type: method
    method: validatePhoneNumber
    options:
      # Options passed to method via opts parameter
      strictMode: true

states:
  checkPhone:
    action:
      - name: validatePhone
```

**Method Return Commands:**
- `updateContext` - Update conversation context
- `continue` - Proceed to next action
- `transit` - Transition to another state
- `done` - End state execution

### Pattern 8: Conditional Actions

Execute actions based on conditions:

```yaml
actions:
  successMessage:
    type: text
    condition: 'data.apiSuccess == true'
    options:
      text: "Operation completed successfully!"

  errorMessage:
    type: text
    condition: 'data.apiSuccess == false'
    options:
      text: "Sorry, an error occurred. Please try again."

states:
  processResult:
    action:
      - name: successMessage
      - name: errorMessage
```

**Condition Syntax:**
- Must return boolean
- Can reference context, data, metadata
- Evaluated in order

### Pattern 9: Multi-Channel Actions

Different actions for different channels:

```yaml
actions:
  menuWhatsApp:
    type: template
    condition: 'metadata.channelType == "whatsapp"'
    options:
      body: "Select an option:"
      buttons:
        - type: postback
          label: "Option 1"
          payload: { action: "opt1" }

  menuWeb:
    type: text
    condition: 'metadata.channelType == "qiscus"'
    options:
      text: "Please type: 1 for Option 1, 2 for Option 2"

states:
  showMenu:
    action:
      - name: menuWhatsApp
      - name: menuWeb
```

### Pattern 10: Scheduler Actions

Create timed messages:

```yaml
actions:
  scheduleTimeout:
    type: api
    options:
      method: POST
      uri: $(config.taptalkSchedulerUrl)
      headers:
        Content-Type: application/json
      body:
        scheduleId: timeout_$(metadata.sessionId)
        userId: $(metadata.userId)
        botId: $(config.botId)
        channelId: $(metadata.channelId)
        timeInMinutes: 5
        command: scheduleRunTimeout
      mapping: {}

  cancelSchedule:
    type: api
    options:
      method: DELETE
      uri: $(config.taptalkSchedulerUrl)/timeout_$(metadata.sessionId)
      headers:
        Content-Type: application/json
      mapping: {}

states:
  awaitResponse:
    action:
      - name: scheduleTimeout  # Start 5-minute timer

  completed:
    action:
      - name: cancelSchedule  # Cancel timer
```

## Action Sequencing

Actions execute in order within a state:

```yaml
states:
  processOrder:
    action:
      - name: validateOrder      # 1. Validate first
      - name: callPaymentAPI     # 2. Then call API
      - name: sendConfirmation   # 3. Then send message
      - name: scheduleReminder   # 4. Finally schedule reminder
```

**Important:** All actions in a state execute before transitions are evaluated.

## Data Mapping

Transform API responses or method results:

```yaml
actions:
  getUserData:
    type: api
    options:
      method: GET
      uri: https://api.example.com/users/$(context.userId)
      mapping:
        # Map to context
        context:
          userName: $(result.response.body.name)
          userEmail: $(result.response.body.email)
        # Map to data
        data:
          accountType: $(result.response.body.account_type)
          joinDate: $(result.response.body.created_at)
          # Transform data with expressions
          isPremiurn: $(result.response.body.account_type == "premium")
```

**Mapping Scopes:**
- `context` - Persistent across conversation
- `data` - Current flow data
- `metadata` - System metadata (avoid modifying)

## WhatsApp Interactive Message Specs

### Button Template Limits
- Max 3 buttons
- Label max 20 characters
- Works on WhatsApp only

### List Template Limits
- Max 10 sections
- Max 10 rows per section
- Title max 24 characters
- Description max 72 characters
- Works on WhatsApp only

### Quick Reply Limits
- Max 13 quick replies
- Label max 20 characters
- Works on most channels

## API Action Configuration

### HTTP Methods
```yaml
method: GET     # Retrieve data
method: POST    # Create/submit data
method: PUT     # Update data
method: PATCH   # Partial update
method: DELETE  # Delete data
```

### Headers
```yaml
headers:
  Authorization: "Bearer $(config.apiToken)"
  Content-Type: "application/json"
  X-Custom-Header: "value"
  Accept: "application/json"
```

### Body (POST/PUT/PATCH)
```yaml
body:
  # JSON object
  field1: value
  field2: $(context.variable)
  nested:
    field3: $(data.field)
```

### Query Parameters
```yaml
uri: https://api.example.com/search?query=$(context.searchTerm)&limit=10
```

### Response Mapping
```yaml
mapping:
  data:
    # Direct field
    userId: $(result.response.body.id)

    # Nested field
    userName: $(result.response.body.user.name)

    # Array element
    firstItem: $(result.response.body.items[0].name)

    # Status check
    success: $(result.response.status == 200)

    # Conditional mapping
    errorMessage: $(result.response.status >= 400 ? result.response.body.error : null)
```

## Method Action Return Types

### Update Context
```javascript
return {
  command: 'updateContext',
  payload: {
    field1: value1,
    field2: value2
  }
};
```

### Update Data
```javascript
return {
  command: 'updateData',
  payload: {
    field1: value1
  }
};
```

### Transit to Another State
```javascript
return {
  command: 'transit',
  args: ['flowName', 'stateName']
};
```

### Continue Execution
```javascript
return {
  command: 'continue'
};
```

### Send Message
```javascript
return {
  command: 'sendMessage',
  payload: {
    type: 'text',
    content: 'Message text'
  }
};
```

## Best Practices

### DO:

1. **Use Action Definitions**
   ```yaml
   # Good: Define once, reuse
   actions:
     welcomeText:
       type: text
       options:
         text: "Welcome!"

   states:
     start:
       action:
         - name: welcomeText
   ```

2. **Validate Before API Calls**
   ```yaml
   states:
     submitData:
       action:
         - name: validateInput    # Validate first
         - name: callAPI          # Then call API
   ```

3. **Handle API Errors**
   ```yaml
   actions:
     apiCall:
       type: api
       options:
         uri: https://api.example.com/data
         mapping:
           data:
             success: $(result.response.status == 200)
             error: $(result.response.status >= 400)
             errorMsg: $(result.response.body.message)
   ```

4. **Use Conditional Messages**
   ```yaml
   actions:
     successMsg:
       type: text
       condition: 'data.success == true'
       options:
         text: "Success!"

     errorMsg:
       type: text
       condition: 'data.success == false'
       options:
         text: "Error: $(data.errorMsg)"
   ```

### DON'T:

1. **Don't Hardcode Values**
   ```yaml
   # Bad: Hardcoded
   uri: https://api.example.com/prod

   # Good: Use config
   uri: $(config.apiBaseUrl)
   ```

2. **Don't Forget Error Handling**
   ```yaml
   # Bad: No error handling
   mapping:
     data:
       result: $(result.response.body.data)

   # Good: Check status
   mapping:
     data:
       result: $(result.response.status == 200 ? result.response.body.data : null)
       error: $(result.response.status >= 400)
   ```

3. **Don't Exceed WhatsApp Limits**
   ```yaml
   # Bad: 4 buttons (max is 3)
   buttons:
     - label: "Option 1"
     - label: "Option 2"
     - label: "Option 3"
     - label: "Option 4"  # Won't work!
   ```

4. **Don't Mix Action Types**
   ```yaml
   # Bad: Confusing structure
   actions:
     mixedAction:
       type: text
       method: someMethod  # Wrong! Can't use method with text type
   ```

## Common Patterns

### Pattern: Loading Message + API + Result

```yaml
states:
  fetchData:
    action:
      - name: loadingMsg
      - name: apiCall
      - name: successMsg
      - name: errorMsg

actions:
  loadingMsg:
    type: text
    options:
      text: "Please wait, fetching your data..."

  apiCall:
    type: api
    options:
      method: GET
      uri: $(config.apiUrl)/data
      mapping:
        data:
          apiSuccess: $(result.response.status == 200)
          apiData: $(result.response.body)

  successMsg:
    type: text
    condition: 'data.apiSuccess == true'
    options:
      text: "Data retrieved successfully!"

  errorMsg:
    type: text
    condition: 'data.apiSuccess == false'
    options:
      text: "Failed to retrieve data. Please try again."
```

### Pattern: Method + Conditional Response

```yaml
methods:
  processInput:
    code: |
      function processInput(msg, ctx, dat, opts, cfg, result) {
        var input = ctx.userInput;
        var isValid = input.length >= 5;

        return {
          command: 'updateData',
          payload: {
            inputValid: isValid,
            errorReason: isValid ? null : 'Input too short'
          }
        };
      }

states:
  validate:
    action:
      - name: runValidation
      - name: validMsg
      - name: invalidMsg

actions:
  runValidation:
    type: method
    method: processInput

  validMsg:
    type: text
    condition: 'data.inputValid == true'
    options:
      text: "Input accepted!"

  invalidMsg:
    type: text
    condition: 'data.inputValid == false'
    options:
      text: "Invalid input: $(data.errorReason)"
```

### Pattern: Multi-Step API Workflow

```yaml
states:
  createOrder:
    action:
      - name: validateUser
      - name: checkInventory
      - name: createPayment
      - name: sendConfirmation

actions:
  validateUser:
    type: api
    options:
      method: GET
      uri: $(config.apiUrl)/users/$(context.userId)
      mapping:
        context:
          userValid: $(result.response.status == 200)

  checkInventory:
    type: api
    condition: 'context.userValid == true'
    options:
      method: POST
      uri: $(config.apiUrl)/inventory/check
      body:
        productId: $(data.productId)
        quantity: $(data.quantity)
      mapping:
        data:
          inStock: $(result.response.body.available)

  createPayment:
    type: api
    condition: 'data.inStock == true'
    options:
      method: POST
      uri: $(config.apiUrl)/payments
      body:
        userId: $(context.userId)
        amount: $(data.totalAmount)
      mapping:
        data:
          paymentId: $(result.response.body.payment_id)
          paymentUrl: $(result.response.body.payment_url)

  sendConfirmation:
    type: text
    condition: 'typeof data.paymentId != "undefined"'
    options:
      text: |
        Order created successfully!
        Payment ID: $(data.paymentId)
        Please complete payment: $(data.paymentUrl)
```

## Action Template

```yaml
actions:
  actionName:
    type: text                    # text, template, api, method
    condition: 'true'             # Optional boolean expression
    options:
      # For text:
      text: "Message text with $(variables)"

      # For template (buttons):
      # header: "Header text"
      # body: "Body text"
      # buttons:
      #   - type: postback
      #     label: "Button Label"
      #     payload:
      #       postback: "intentName"
      #       field: value

      # For template (list):
      # header: "Header"
      # body: "Body"
      # button: "View Options"
      # list:
      #   sections:
      #     - title: "Section Title"
      #       rows:
      #         - title: "Row Title"
      #           description: "Description"
      #           value:
      #             postback: "intentName"
      #             field: value

      # For api:
      # method: GET
      # uri: url
      # headers:
      #   Header-Name: value
      # body:
      #   field: value
      # mapping:
      #   data:
      #     field: $(result.response.body.field)

    # For method type:
    # method: methodName
```

## Debugging Actions

### Issue: Action Not Executing

**Check:**
1. Condition evaluates to true
2. Action is in state's action list
3. Action definition exists
4. Syntax is valid YAML

### Issue: API Call Failing

**Debug:**
```yaml
actions:
  debugApi:
    type: api
    options:
      method: GET
      uri: $(config.apiUrl)/test
      mapping:
        data:
          statusCode: $(result.response.status)
          headers: $(result.response.headers)
          body: $(result.response.body)
          error: $(result.error)
```

### Issue: Variables Not Interpolating

**Common mistakes:**
```yaml
# Wrong: Missing $
text: "(context.userName)"

# Wrong: Wrong brackets
text: "${context.userName}"

# Correct:
text: "$(context.userName)"
```

## Summary

When building actions:
1. Define reusable action blocks
2. Use conditional execution
3. Validate before API calls
4. Map API responses to data/context
5. Handle errors gracefully
6. Respect WhatsApp template limits
7. Use config for URLs and tokens
8. Test with different channels
9. Clean up schedulers
10. Keep actions focused (single responsibility)

Remember: Actions are what users see and experience - make them clear, reliable, and helpful.
