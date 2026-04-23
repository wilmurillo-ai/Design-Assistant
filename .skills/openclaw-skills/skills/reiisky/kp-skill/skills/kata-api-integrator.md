# Kata API Integrator Skill

Expert skill for integrating external APIs in Kata Platform YAML bots - HTTP requests, authentication, response parsing, and error handling.

## When to Use This Skill

Use this skill when you need to:
- Integrate third-party REST APIs
- Make HTTP requests (GET, POST, PUT, DELETE, PATCH)
- Handle API authentication (Bearer, API Key, Basic Auth)
- Parse and map JSON responses
- Handle API errors and retry logic
- Transform API data for bot context
- Debug API integration issues
- Implement API rate limiting strategies

## API Action Fundamentals

API actions in Kata Platform allow you to make HTTP requests to external services and integrate their responses into your conversation flow.

### Basic API Action Structure

```yaml
actions:
  actionName:
    type: api
    options:
      method: GET                    # HTTP method
      uri: https://api.example.com   # Endpoint URL
      headers:                       # HTTP headers
        Header-Name: value
      body:                          # Request body (POST/PUT/PATCH)
        field: value
      mapping:                       # Response mapping
        data:
          field: $(result.response.body.field)
```

## HTTP Methods

### GET - Retrieve Data

```yaml
actions:
  getUserProfile:
    type: api
    options:
      method: GET
      uri: https://api.example.com/users/$(context.userId)
      headers:
        Authorization: "Bearer $(config.apiToken)"
        Accept: application/json
      mapping:
        context:
          userName: $(result.response.body.name)
          userEmail: $(result.response.body.email)
        data:
          accountType: $(result.response.body.account_type)
          balance: $(result.response.body.balance)
```

**When to use:**
- Fetching user data
- Retrieving lists or catalogs
- Checking status
- Searching/querying data

### POST - Create/Submit Data

```yaml
actions:
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
        subject: $(data.issueSubject)
        description: $(data.issueDescription)
        priority: high
        category: technical
      mapping:
        data:
          ticketNumber: $(result.response.body.ticket_number)
          ticketId: $(result.response.body.id)
          status: $(result.response.body.status)
          createdAt: $(result.response.body.created_at)
```

**When to use:**
- Creating new records
- Submitting forms
- Triggering actions
- Uploading data

### PUT - Update Data (Full Replace)

```yaml
actions:
  updateUserProfile:
    type: api
    options:
      method: PUT
      uri: https://api.example.com/users/$(context.userId)
      headers:
        Authorization: "Bearer $(config.apiToken)"
        Content-Type: application/json
      body:
        name: $(context.userName)
        email: $(context.userEmail)
        phone: $(context.userPhone)
        address: $(context.userAddress)
      mapping:
        context:
          profileUpdated: $(result.response.status == 200)
```

**When to use:**
- Replacing entire resource
- Full profile updates
- Complete data overwrites

### PATCH - Partial Update

```yaml
actions:
  updateTicketStatus:
    type: api
    options:
      method: PATCH
      uri: https://api.example.com/tickets/$(data.ticketId)
      headers:
        Authorization: "Bearer $(config.apiToken)"
        Content-Type: application/json
      body:
        status: resolved
        resolution_notes: $(data.resolutionNotes)
      mapping:
        data:
          updated: $(result.response.status == 200)
```

**When to use:**
- Updating specific fields
- Status changes
- Partial modifications

### DELETE - Remove Data

```yaml
actions:
  cancelScheduler:
    type: api
    options:
      method: DELETE
      uri: $(config.schedulerUrl)/$(data.schedulerId)
      headers:
        Authorization: "Bearer $(config.apiToken)"
      mapping:
        data:
          cancelled: $(result.response.status == 204)
```

**When to use:**
- Deleting resources
- Cancelling schedulers
- Removing records

## Authentication Patterns

### Bearer Token

```yaml
actions:
  apiWithBearer:
    type: api
    options:
      method: GET
      uri: https://api.example.com/data
      headers:
        Authorization: "Bearer $(config.apiToken)"
        Content-Type: application/json
```

**Best Practice:** Store token in `config` (bot.yml):
```yaml
config:
  apiToken: "your-secret-token-here"
```

### API Key (Header)

```yaml
actions:
  apiWithKey:
    type: api
    options:
      method: GET
      uri: https://api.example.com/data
      headers:
        X-API-Key: $(config.apiKey)
        Content-Type: application/json
```

### API Key (Query Parameter)

```yaml
actions:
  apiWithQueryKey:
    type: api
    options:
      method: GET
      uri: https://api.example.com/data?api_key=$(config.apiKey)
      headers:
        Content-Type: application/json
```

### Basic Auth

```yaml
actions:
  apiWithBasicAuth:
    type: api
    options:
      method: GET
      uri: https://api.example.com/data
      headers:
        # Base64 encode "username:password"
        Authorization: "Basic $(config.basicAuthToken)"
        Content-Type: application/json
```

### OAuth 2.0 (Refresh Token Flow)

```yaml
methods:
  refreshAccessToken:
    code: |
      function refreshAccessToken(msg, ctx, dat, opts, cfg, result) {
        // This would be called via API action to refresh token
        // Store new token in context
        return {
          command: 'updateContext',
          payload: {
            accessToken: result.response.body.access_token,
            tokenExpiresAt: Date.now() + (result.response.body.expires_in * 1000)
          }
        };
      }

actions:
  refreshToken:
    type: api
    options:
      method: POST
      uri: https://oauth.example.com/token
      headers:
        Content-Type: application/x-www-form-urlencoded
      body:
        grant_type: refresh_token
        refresh_token: $(context.refreshToken)
        client_id: $(config.oauthClientId)
        client_secret: $(config.oauthClientSecret)
    mapping:
      context:
        accessToken: $(result.response.body.access_token)

  useProtectedApi:
    type: api
    options:
      method: GET
      uri: https://api.example.com/protected
      headers:
        Authorization: "Bearer $(context.accessToken)"
```

## Response Mapping

### Simple Field Mapping

```yaml
mapping:
  data:
    # Direct field access
    userId: $(result.response.body.id)
    userName: $(result.response.body.name)

    # HTTP status
    statusCode: $(result.response.status)

    # Success check
    success: $(result.response.status == 200)
```

### Nested Field Access

```yaml
mapping:
  data:
    # Nested object
    street: $(result.response.body.address.street)
    city: $(result.response.body.address.city)

    # Deep nesting
    mainPhone: $(result.response.body.contact.phones.primary.number)
```

### Array Handling

```yaml
mapping:
  data:
    # First element
    firstItem: $(result.response.body.items[0].name)

    # Specific index
    secondItem: $(result.response.body.items[1].name)

    # Array length
    itemCount: $(result.response.body.items.length)
```

**Note:** Kata Platform mapping doesn't support loops. For complex array processing, use a method:

```javascript
function processArrayResponse(msg, ctx, dat, opts, cfg, result) {
  var items = result.response.body.items;
  var processed = [];

  for (var i = 0; i < items.length; i++) {
    processed.push({
      id: items[i].id,
      name: items[i].name,
      price: items[i].price
    });
  }

  return {
    command: 'updateData',
    payload: {
      processedItems: processed,
      totalItems: items.length
    }
  };
}
```

### Conditional Mapping

```yaml
mapping:
  data:
    # Ternary operator
    displayName: $(result.response.body.name ? result.response.body.name : "Unknown")

    # Status check
    errorMessage: $(result.response.status >= 400 ? result.response.body.message : null)

    # Null coalescing (manual)
    email: $(result.response.body.email ? result.response.body.email : context.defaultEmail)
```

### Multi-Scope Mapping

```yaml
mapping:
  # Map to context (persistent)
  context:
    userId: $(result.response.body.user_id)
    authenticated: true

  # Map to data (flow-scoped)
  data:
    currentBalance: $(result.response.body.balance)
    lastTransaction: $(result.response.body.last_transaction)

  # Note: Avoid mapping to metadata (system-managed)
```

## Error Handling

### HTTP Status Checks

```yaml
actions:
  apiWithErrorHandling:
    type: api
    options:
      method: GET
      uri: https://api.example.com/data
      headers:
        Authorization: "Bearer $(config.apiToken)"
      mapping:
        data:
          # Check various status codes
          success: $(result.response.status == 200)
          notFound: $(result.response.status == 404)
          unauthorized: $(result.response.status == 401)
          serverError: $(result.response.status >= 500)

          # Extract error details
          errorCode: $(result.response.status >= 400 ? result.response.body.error_code : null)
          errorMessage: $(result.response.status >= 400 ? result.response.body.message : null)

states:
  callApi:
    action:
      - name: apiWithErrorHandling
      - name: successResponse
      - name: notFoundResponse
      - name: errorResponse

actions:
  successResponse:
    type: text
    condition: 'data.success == true'
    options:
      text: "Data retrieved successfully!"

  notFoundResponse:
    type: text
    condition: 'data.notFound == true'
    options:
      text: "Resource not found. Please check your input."

  errorResponse:
    type: text
    condition: 'data.success == false && data.notFound == false'
    options:
      text: "An error occurred: $(data.errorMessage)"
```

### Network Error Handling

```yaml
mapping:
  data:
    # Check if request succeeded
    networkError: $(typeof result.error != "undefined")
    errorDetails: $(result.error ? result.error.message : null)

    # Safe response access
    responseData: $(result.response ? result.response.body : null)
```

### Timeout Configuration

```yaml
# Note: Kata Platform has default timeouts
# For long-running operations, consider:
# 1. Async webhook patterns
# 2. Polling mechanisms
# 3. Background job queues

actions:
  longRunningApi:
    type: api
    options:
      method: POST
      uri: https://api.example.com/long-process
      body:
        task: processData
        callback_url: $(config.webhookUrl)
      mapping:
        data:
          jobId: $(result.response.body.job_id)

  checkJobStatus:
    type: api
    options:
      method: GET
      uri: https://api.example.com/jobs/$(data.jobId)
      mapping:
        data:
          jobStatus: $(result.response.body.status)
          jobComplete: $(result.response.body.status == "completed")
```

## Common Integration Patterns

### Pattern 1: Search/Filter API

```yaml
actions:
  searchProducts:
    type: api
    options:
      method: GET
      uri: https://api.example.com/products?search=$(context.searchQuery)&category=$(data.selectedCategory)&limit=10
      headers:
        Authorization: "Bearer $(config.apiToken)"
      mapping:
        data:
          searchResults: $(result.response.body.products)
          totalResults: $(result.response.body.total)
          hasMore: $(result.response.body.total > 10)

states:
  showResults:
    action:
      - name: searchProducts
      - name: displayResults
      - name: noResults

actions:
  displayResults:
    type: text
    condition: 'data.totalResults > 0'
    options:
      text: "Found $(data.totalResults) products matching '$(context.searchQuery)'"

  noResults:
    type: text
    condition: 'data.totalResults == 0'
    options:
      text: "No products found for '$(context.searchQuery)'. Try a different search."
```

### Pattern 2: Multi-Step API Workflow

```yaml
states:
  createOrder:
    action:
      - name: validateCustomer
      - name: checkInventory
      - name: calculatePrice
      - name: createPayment
      - name: finalConfirmation

actions:
  validateCustomer:
    type: api
    options:
      method: GET
      uri: https://api.example.com/customers/$(context.customerId)
      mapping:
        context:
          customerValid: $(result.response.status == 200)
          customerName: $(result.response.body.name)

  checkInventory:
    type: api
    condition: 'context.customerValid == true'
    options:
      method: POST
      uri: https://api.example.com/inventory/check
      body:
        product_id: $(data.productId)
        quantity: $(data.quantity)
      mapping:
        data:
          inStock: $(result.response.body.available == true)
          availableQty: $(result.response.body.quantity)

  calculatePrice:
    type: api
    condition: 'data.inStock == true'
    options:
      method: POST
      uri: https://api.example.com/pricing/calculate
      body:
        product_id: $(data.productId)
        quantity: $(data.quantity)
        customer_id: $(context.customerId)
      mapping:
        data:
          totalPrice: $(result.response.body.total)
          discount: $(result.response.body.discount)

  createPayment:
    type: api
    condition: 'typeof data.totalPrice != "undefined"'
    options:
      method: POST
      uri: https://api.example.com/payments
      body:
        customer_id: $(context.customerId)
        amount: $(data.totalPrice)
        currency: IDR
      mapping:
        data:
          paymentId: $(result.response.body.payment_id)
          paymentUrl: $(result.response.body.payment_url)
```

### Pattern 3: Pagination

```yaml
actions:
  fetchPage:
    type: api
    options:
      method: GET
      uri: https://api.example.com/items?page=$(data.currentPage)&per_page=10
      mapping:
        data:
          items: $(result.response.body.items)
          currentPage: $(result.response.body.page)
          totalPages: $(result.response.body.total_pages)
          hasNextPage: $(result.response.body.page < result.response.body.total_pages)

states:
  showItems:
    action:
      - name: fetchPage
      - name: displayItems
      - name: showNextOption

actions:
  displayItems:
    type: text
    options:
      text: "Showing page $(data.currentPage) of $(data.totalPages)"

  showNextOption:
    type: template
    condition: 'data.hasNextPage == true'
    options:
      body: "View more items?"
      buttons:
        - type: postback
          label: "Next Page"
          payload:
            postback: "nextPage"
            page: $(data.currentPage + 1)
```

### Pattern 4: Webhook Registration

```yaml
actions:
  registerWebhook:
    type: api
    options:
      method: POST
      uri: https://api.example.com/webhooks
      body:
        url: $(config.webhookUrl)/callback
        events:
          - payment.success
          - payment.failed
          - order.completed
        secret: $(config.webhookSecret)
      mapping:
        context:
          webhookId: $(result.response.body.webhook_id)
          webhookActive: true
```

### Pattern 5: File Upload (Base64)

```yaml
methods:
  encodeFileToBase64:
    code: |
      function encodeFileToBase64(msg, ctx, dat, opts, cfg, result) {
        // Assuming you have file data
        var fileContent = dat.fileContent;
        var base64 = btoa(fileContent);  // ES5 encoding

        return {
          command: 'updateData',
          payload: {
            fileBase64: base64
          }
        };
      }

actions:
  uploadFile:
    type: api
    options:
      method: POST
      uri: https://api.example.com/uploads
      headers:
        Content-Type: application/json
      body:
        filename: $(data.fileName)
        content: $(data.fileBase64)
        content_type: $(data.fileType)
      mapping:
        data:
          fileUrl: $(result.response.body.url)
          fileId: $(result.response.body.id)
```

## Scheduler API Integration

### Create Scheduler

```yaml
actions:
  scheduleReminder:
    type: api
    options:
      method: POST
      uri: $(config.taptalkSchedulerUrl)
      headers:
        Content-Type: application/json
      body:
        scheduleId: reminder_$(metadata.sessionId)
        userId: $(metadata.userId)
        botId: $(config.botId)
        channelId: $(metadata.channelId)
        timeInMinutes: 10
        command: scheduleRunReminder
      mapping:
        context:
          reminderScheduled: $(result.response.status == 200)
          schedulerId: reminder_$(metadata.sessionId)
```

### Cancel Scheduler

```yaml
actions:
  cancelReminder:
    type: api
    options:
      method: DELETE
      uri: $(config.taptalkSchedulerUrl)/$(context.schedulerId)
      headers:
        Content-Type: application/json
      mapping:
        context:
          reminderScheduled: false
          schedulerId: null
```

## Best Practices

### DO:

1. **Store Credentials in Config**
   ```yaml
   # bot.yml
   config:
     apiToken: "secret-token"
     apiBaseUrl: "https://api.example.com"

   # In actions
   uri: $(config.apiBaseUrl)/endpoint
   headers:
     Authorization: "Bearer $(config.apiToken)"
   ```

2. **Check Status Codes**
   ```yaml
   mapping:
     data:
       success: $(result.response.status == 200)
       created: $(result.response.status == 201)
       error: $(result.response.status >= 400)
   ```

3. **Handle Network Errors**
   ```yaml
   mapping:
     data:
       networkError: $(typeof result.error != "undefined")
       data: $(result.response ? result.response.body : null)
   ```

4. **Use Descriptive Action Names**
   ```yaml
   # Good
   actions:
     getUserBillingHistory:
     createSupportTicket:
     updatePaymentStatus:

   # Bad
   actions:
     api1:
     callApi:
     doRequest:
   ```

5. **Map Only Needed Fields**
   ```yaml
   # Good: Map specific fields
   mapping:
     data:
       userId: $(result.response.body.id)
       userName: $(result.response.body.name)

   # Avoid: Mapping entire response
   # (Can cause data bloat)
   ```

### DON'T:

1. **Don't Hardcode URLs**
   ```yaml
   # Bad
   uri: https://api.production.com/data

   # Good
   uri: $(config.apiBaseUrl)/data
   ```

2. **Don't Expose Secrets**
   ```yaml
   # Bad
   headers:
     Authorization: "Bearer sk_live_abc123xyz"

   # Good
   headers:
     Authorization: "Bearer $(config.apiToken)"
   ```

3. **Don't Ignore Errors**
   ```yaml
   # Bad: No error handling
   mapping:
     data:
       result: $(result.response.body.data)

   # Good: Check for errors
   mapping:
     data:
       success: $(result.response.status == 200)
       result: $(result.response.status == 200 ? result.response.body.data : null)
       error: $(result.response.status >= 400 ? result.response.body.message : null)
   ```

4. **Don't Trust External Data**
   ```yaml
   # Bad: Direct usage without validation
   text: "Welcome $(result.response.body.name)!"

   # Good: Validate or provide fallback
   text: "Welcome $(result.response.body.name ? result.response.body.name : 'User')!"
   ```

## Debugging API Issues

### 1. Log Full Response

```yaml
actions:
  debugApi:
    type: api
    options:
      method: GET
      uri: https://api.example.com/test
      mapping:
        data:
          fullResponse: $(result)
          statusCode: $(result.response.status)
          headers: $(result.response.headers)
          body: $(result.response.body)
          error: $(result.error)
```

### 2. Use Method for Complex Debugging

```javascript
function debugApiCall(msg, ctx, dat, opts, cfg, result) {
  console.log('=== API Debug ===');
  console.log('Status:', result.response.status);
  console.log('Headers:', JSON.stringify(result.response.headers));
  console.log('Body:', JSON.stringify(result.response.body));
  console.log('Error:', result.error);
  console.log('===============');

  return { command: 'continue' };
}
```

### 3. Test with Simple Endpoint First

```yaml
actions:
  testConnection:
    type: api
    options:
      method: GET
      uri: https://httpbin.org/get
      mapping:
        data:
          testSuccess: $(result.response.status == 200)
```

## API Integration Checklist

- [ ] API credentials stored in `config`
- [ ] All endpoints use config variables for base URL
- [ ] HTTP status codes checked in mapping
- [ ] Network errors handled
- [ ] Required fields validated before API call
- [ ] Response fields safely accessed (null checks)
- [ ] Error messages mapped for user feedback
- [ ] Authentication headers included
- [ ] Content-Type header set correctly
- [ ] Request body structure matches API spec
- [ ] Response mapped to appropriate scope (context vs data)
- [ ] Timeout scenarios considered
- [ ] Rate limiting handled if applicable

## Summary

When integrating APIs:
1. Always use config for credentials and URLs
2. Check HTTP status codes in mapping
3. Handle network and API errors gracefully
4. Map only needed fields to avoid bloat
5. Validate data before sending
6. Use methods for complex response processing
7. Test with simple endpoints first
8. Log full responses when debugging
9. Consider async patterns for long operations
10. Document API dependencies and requirements

Remember: External APIs are unreliable - always expect failures and handle them gracefully.
