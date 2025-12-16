<img width="3436" height="568" alt="image" src="https://github.com/user-attachments/assets/b41f8ae2-f4b1-4d86-8263-8ed97b69ffaf" />
# AWS API Gateway & Lambda - Comprehensive Guide

A complete reference guide for building, deploying, and securing APIs using AWS API Gateway and Lambda functions.

## Table of Contents

- [Overview](#overview)
- [Core Concepts](#core-concepts)
- [Getting Started](#getting-started)
- [Integration Patterns](#integration-patterns)
- [Request Validation](#request-validation)
- [Security](#security)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

### What is API Gateway?

AWS API Gateway is a fully managed service that acts as the "front door" for your applications. It handles accepting and processing concurrent API calls, routing them to backend services like Lambda, EC2, or HTTP endpoints.

### Key Benefits

- **Scalability**: Automatically handles traffic spikes
- **Security**: Built-in throttling, authorization, and access control
- **Versioning**: Support for multiple API versions
- **Monitoring**: Native CloudWatch integration
- **Cost-Effective**: Pay only for API calls received

### API Types Comparison

| Feature | HTTP API | REST API |
|---------|----------|----------|
| **Best For** | Serverless, simple HTTP proxies | Complex, production-grade APIs |
| **Cost** | Lower (~71% cheaper) | Higher |
| **Performance** | Faster | Slightly slower |
| **Authorization** | JWT, OAuth 2.0, IAM | IAM, Lambda Authorizers, Cognito, API Keys |
| **Request Validation** | ❌ | ✅ |
| **Usage Plans** | ❌ | ✅ |
| **API Keys** | ❌ | ✅ |
| **Caching** | ❌ | ✅ |

**Recommendation**: Use HTTP API for simple workloads; REST API for enterprise applications requiring advanced features.

## Core Concepts

### HTTP Methods

| Method | Purpose | Idempotent |
|--------|---------|------------|
| GET | Retrieve data | ✅ |
| POST | Create resource | ❌ |
| PUT | Update/create resource | ✅ |
| PATCH | Partial update | ❌ |
| DELETE | Remove resource | ✅ |

### API Gateway Flow

```
Client Request → API Gateway → Authorization → Backend (Lambda/HTTP) → Response
```

## Getting Started

### Prerequisites

- AWS Account
- AWS CLI configured
- Basic knowledge of Lambda and Python/Node.js

### Step 1: Create a Lambda Function

**Python Example**:

```python
import json

def lambda_handler(event, context):
    # Extract query parameter
    name = "World"
    if event.get('queryStringParameters'):
        name = event.get('queryStringParameters').get('name', name)
    
    # Build response
    response_data = {
        "message": f"Hello, {name}! Your request was successful.",
        "status": "success"
    }
    
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"  # CORS
        },
        "body": json.dumps(response_data)
    }
```

**Node.js Example**:

```javascript
exports.handler = async (event) => {
    const name = event.queryStringParameters?.name || 'World';
    
    return {
        statusCode: 200,
        headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        body: JSON.stringify({
            message: `Hello, ${name}! Your request was successful.`,
            status: 'success'
        })
    };
};
```

### Step 2: Create REST API

1. Navigate to **API Gateway Console**
2. Click **Create API**
3. Choose **REST API** → **Build**
4. Select **New API**
5. Enter API name (e.g., `MyFirstAPI`)
6. Click **Create API**

### Step 3: Create Resource and Method

1. Click **Actions** → **Create Resource**
2. Resource Name: `users`
3. Resource Path: `/users`
4. Click **Create Resource**
5. With resource selected: **Actions** → **Create Method** → **GET**
6. Configure method:
   - Integration Type: **Lambda Function**
   - Use Lambda Proxy Integration: **✅ Checked**
   - Lambda Function: Select your function
7. Click **Save** → **OK** (to grant permissions)

### Step 4: Deploy API

1. Click **Actions** → **Deploy API**
2. Deployment stage: **[New Stage]**
3. Stage name: `dev`
4. Click **Deploy**
5. Copy the **Invoke URL**:
   ```
   https://{api-id}.execute-api.{region}.amazonaws.com/dev
   ```

### Step 5: Test Your API

```bash
curl "https://{api-id}.execute-api.{region}.amazonaws.com/dev/users?name=Asishkumar"
```

**Expected Response**:
```json
{
  "message": "Hello, Asishkumar! Your request was successful.",
  "status": "success"
}
```

## Integration Patterns

### Lambda Proxy Integration (Recommended)

**Advantages**:
- Entire HTTP request passed to Lambda as event
- Simple configuration
- Full control over response format

**Event Structure**:
```json
{
  "resource": "/users",
  "path": "/users",
  "httpMethod": "GET",
  "headers": { ... },
  "queryStringParameters": { "name": "Asishkumar" },
  "body": null,
  "isBase64Encoded": false
}
```

**Lambda Response Format**:
```python
return {
    "statusCode": 200,
    "headers": {"Content-Type": "application/json"},
    "body": json.dumps({"message": "Success"})
}
```

### Lambda Non-Proxy Integration

**Advantages**:
- Fine-grained request/response transformation
- Custom mapping templates
- Backend service independence

**Request Mapping Template** (VTL):
```velocity
#set($inputRoot = $input.json('$'))
#set($originalParam = $inputRoot.name)
#set($prefix = "processed_")
#if(!$originalParam.startsWith($prefix))
  #set($originalParam = $prefix + $originalParam)
#end
{
  "name": "$originalParam",
  "timestamp": "$context.requestTime"
}
```

**Lambda Function**:
```python
def lambda_handler(event, context):
    name = event.get('name', 'Unknown')
    timestamp = event.get('timestamp', '')
    
    return {
        "greeting": f"Hello {name}!",
        "processed_at": timestamp
    }
```

**Response Mapping Template**:
```velocity
{
  "message": "$input.path('$.greeting')",
  "time": "$input.path('$.processed_at')"
}
```

## Request Validation

### Create Request Model

1. In API Gateway: **Models** → **Create**
2. Model name: `UserRequest`
3. Content type: `application/json`
4. Model schema:

```json
{
  "$schema": "http://json-schema.org/draft-04/schema#",
  "title": "UserRequest",
  "type": "object",
  "required": ["name", "email", "phone"],
  "properties": {
    "name": {
      "type": "string",
      "minLength": 1,
      "maxLength": 100
    },
    "email": {
      "type": "string",
      "format": "email"
    },
    "phone": {
      "type": "string",
      "pattern": "^[0-9]{10}$"
    },
    "age": {
      "type": "integer",
      "minimum": 18,
      "maximum": 120
    }
  },
  "additionalProperties": false
}
```

### Apply Validation

1. Select your POST method
2. Click **Method Request**
3. Request Validator: **Validate body**
4. Request Body → **Add model**:
   - Content type: `application/json`
   - Model: `UserRequest`

### Test Invalid Request

```bash
curl -X POST https://{api-id}.execute-api.{region}.amazonaws.com/dev/users \
  -H "Content-Type: application/json" \
  -d '{"name": ""}'
```

**Response** (400 Bad Request):
```json
{
  "message": "Invalid request body"
}
```

## Security

### 1. IAM Resource Policies

**Block Specific IP Address**:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Principal": "*",
      "Action": "execute-api:Invoke",
      "Resource": "arn:aws:execute-api:{region}:{account-id}:{api-id}/*/GET/users",
      "Condition": {
        "IpAddress": {
          "aws:SourceIp": ["203.0.113.0/24"]
        }
      }
    },
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "execute-api:Invoke",
      "Resource": "arn:aws:execute-api:{region}:{account-id}:{api-id}/*/GET/users"
    }
  ]
}
```

**Allow Only From VPC Endpoint**:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "execute-api:Invoke",
      "Resource": "arn:aws:execute-api:{region}:{account-id}:{api-id}/*",
      "Condition": {
        "StringEquals": {
          "aws:SourceVpce": "vpce-1234567890abcdef0"
        }
      }
    }
  ]
}
```

### 2. Lambda Authorizers (Custom Authorization)

**Flow**:
```
Client → API Gateway → Lambda Authorizer → Policy Decision → Backend Lambda
```

**Authorizer Lambda**:

```python
import json

def generate_policy(principal_id, effect, resource):
    """Generate IAM policy for API Gateway"""
    return {
        "principalId": principal_id,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [{
                "Action": "execute-api:Invoke",
                "Effect": effect,
                "Resource": resource
            }]
        },
        "context": {
            "userId": principal_id,
            "role": "admin"  # Pass additional context
        }
    }

def lambda_handler(event, context):
    # Extract token from Authorization header
    token = event.get('authorizationToken', '')
    method_arn = event['methodArn']
    
    # Validate token (replace with real validation)
    if token == "Bearer mysecrettoken":
        return generate_policy("user123", "Allow", method_arn)
    
    # Deny access
    return generate_policy("user", "Deny", method_arn)
```

**Configure Authorizer**:

1. API Gateway → **Authorizers** → **Create New Authorizer**
2. Name: `CustomAuthorizer`
3. Type: **Lambda**
4. Lambda Function: Select your authorizer
5. Lambda Event Payload: **Token**
6. Token Source: `Authorization`
7. Authorization Caching: **Enabled** (300 seconds)

**Attach to Method**:

1. Select your method → **Method Request**
2. Authorization: Select `CustomAuthorizer`
3. Deploy API

**Test**:

```bash
# Success
curl -H "Authorization: Bearer mysecrettoken" \
  https://{api-id}.execute-api.{region}.amazonaws.com/dev/users

# Failure (401 Unauthorized)
curl -H "Authorization: Bearer wrongtoken" \
  https://{api-id}.execute-api.{region}.amazonaws.com/dev/users
```

### 3. API Keys & Usage Plans

**Create API Key**:

1. API Gateway → **API Keys** → **Create API Key**
2. Name: `ProductionKey`
3. Save the key value

**Create Usage Plan**:

1. **Usage Plans** → **Create**
2. Name: `BasicPlan`
3. Throttling:
   - Rate: 1000 requests/second
   - Burst: 2000 requests
4. Quota: 10000 requests/month
5. Add API Stage
6. Add API Key to plan

**Require API Key**:

1. Method → **Method Request**
2. API Key Required: **true**
3. Deploy API

**Test**:

```bash
curl -H "x-api-key: YOUR_API_KEY" \
  https://{api-id}.execute-api.{region}.amazonaws.com/dev/users
```

## Best Practices

### Performance

- **Enable Caching**: Reduce latency and backend load
  ```
  Stage → Settings → Cache Settings → Enable API cache
  Cache capacity: 0.5 GB to 237 GB
  TTL: 300 seconds (default)
  ```

- **Use Lambda Proxy Integration**: Simpler and more efficient

- **Minimize Cold Starts**:
  - Use provisioned concurrency for Lambda
  - Keep Lambda packages small
  - Use appropriate memory allocation

### Security

- ✅ Always use HTTPS endpoints
- ✅ Implement request validation
- ✅ Use least privilege IAM policies
- ✅ Enable CloudWatch Logs
- ✅ Rotate API keys regularly
- ✅ Use AWS WAF for DDoS protection
- ✅ Enable throttling limits

### Cost Optimization

- Use HTTP APIs for simple use cases (71% cheaper)
- Enable caching for read-heavy workloads
- Set appropriate throttling limits
- Monitor usage with CloudWatch
- Delete unused APIs and stages

### Monitoring

**Enable CloudWatch Logs**:

1. Stage → **Logs/Tracing**
2. CloudWatch Settings:
   - Enable CloudWatch Logs: ✅
   - Log level: INFO
   - Log full requests/responses: ✅

**Key Metrics to Monitor**:

- **Count**: Total API requests
- **4XXError**: Client errors
- **5XXError**: Server errors
- **Latency**: Response time
- **IntegrationLatency**: Backend response time
- **CacheHitCount**: Cache efficiency

**Create Alarms**:

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "HighErrorRate" \
  --metric-name 5XXError \
  --namespace AWS/ApiGateway \
  --statistic Sum \
  --period 300 \
  --evaluation-periods 1 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold
```

## Troubleshooting

### Common Issues

#### 1. 403 Forbidden

**Causes**:
- Missing IAM permissions
- Resource policy blocking request
- API key required but not provided
- Lambda authorizer denying access

**Solutions**:
- Check Lambda execution role has `lambda:InvokeFunction`
- Review resource policy
- Verify API key in `x-api-key` header
- Check authorizer logs

#### 2. 502 Bad Gateway

**Causes**:
- Lambda timeout
- Lambda function error
- Invalid response format

**Solutions**:
- Increase Lambda timeout (max 29 seconds for API Gateway)
- Check Lambda logs in CloudWatch
- Ensure Lambda returns proper format:
  ```python
  {
    "statusCode": 200,
    "headers": {...},
    "body": "..."  # Must be string
  }
  ```

#### 3. 504 Gateway Timeout

**Causes**:
- Lambda execution exceeds 29 seconds
- Integration timeout

**Solutions**:
- Optimize Lambda code
- Use asynchronous processing for long tasks
- Reduce integration timeout in method settings

#### 4. CORS Errors

**Solution** - Add CORS headers in Lambda:

```python
return {
    "statusCode": 200,
    "headers": {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type,Authorization"
    },
    "body": json.dumps(response)
}
```

Or enable CORS in API Gateway: **Actions** → **Enable CORS**

### Debugging Tips

1. **Enable Execution Logs**: Detailed request/response data
2. **Use X-Ray Tracing**: Track request flow
3. **Test in Console**: Built-in testing tool
4. **Check Lambda Logs**: CloudWatch Logs Insights
5. **Use Postman/cURL**: Test outside browser

### Useful CloudWatch Logs Insights Queries

**Find Errors**:
```
fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
```

**Analyze Latency**:
```
fields @timestamp, @duration
| stats avg(@duration), max(@duration), min(@duration)
```

## Quick Reference

### AWS CLI Commands

**Create REST API**:
```bash
aws apigateway create-rest-api --name "MyAPI" --region us-east-1
```

**Deploy API**:
```bash
aws apigateway create-deployment \
  --rest-api-id {api-id} \
  --stage-name prod
```

**Get API URL**:
```bash
aws apigateway get-rest-api --rest-api-id {api-id}
```

**Delete API**:
```bash
aws apigateway delete-rest-api --rest-api-id {api-id}
```

### Useful Links

- [API Gateway Documentation](https://docs.aws.amazon.com/apigateway/)
- [Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [VTL Reference](https://velocity.apache.org/engine/devel/vtl-reference.html)
- [JSON Schema Validation](https://json-schema.org/)

## Conclusion

AWS API Gateway combined with Lambda provides a powerful, scalable, and cost-effective solution for building modern APIs. Start with HTTP APIs for simple use cases, and graduate to REST APIs as your requirements grow.

**Next Steps**:
1. Build your first API following this guide
2. Implement authentication with Lambda Authorizers
3. Set up monitoring and alarms
4. Optimize for cost and performance
5. Explore advanced features (WebSocket APIs, HTTP APIs)

---

**Contributing**: Feel free to submit issues and enhancement requests!

**License**: MIT

**Last Updated by Asishkumar**: December 2025


