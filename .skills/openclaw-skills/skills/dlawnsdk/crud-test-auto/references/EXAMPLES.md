# Examples

Real-world configuration examples for different types of services.

## Table of Contents

- [Golf App (Greenlight)](#golf-app-greenlight)
- [E-commerce API](#e-commerce-api)
- [Social Media API](#social-media-api)
- [SaaS Project Management](#saas-project-management)

---

## Golf/Sports App Example

Generic example for golf or sports booking app.

**config-golf-app.json:**
```json
{
  "service": {
    "name": "Golf Booking App",
    "api_base": "https://api.golfapp.example.com"
  },
  
  "auth": {
    "method": "custom",
    "headers": {
      "x-access-token": "{token}",
      "x-access-id": "{user_id}"
    }
  },
  
  "test_account": {
    "email": "test@example.com",
    "password": "your_password",
    "login_endpoint": "/login",
    "token_path": "auth_token",
    "user_id_path": "id"
  },
  
  "features": {
    "community": {
      "name": "Community Posts",
      "create": {
        "endpoint": "/api/community/posts",
        "params": {
          "required": ["userId", "content", "category"],
          "optional": ["media", "tags"]
        },
        "id_field": "data",
        "test_data": {
          "content": "[AutoTest] Test post",
          "category": "general"
        }
      },
      "read": {
        "endpoint": "/api/community/posts",
        "list_path": "data.list"
      },
      "update": {
        "endpoint": "/api/community/posts/{id}",
        "method": "PUT"
      },
      "delete": {
        "endpoint": "/api/community/posts/{id}"
      }
    },
    
    "bookings": {
      "name": "Golf Bookings",
      "create": {
        "endpoint": "/api/bookings",
        "params": {
          "required": ["userId", "course", "datetime"],
          "optional": ["players", "notes"]
        },
        "id_field": "result",
        "test_data": {
          "course": "[AutoTest] Test Golf Club",
          "datetime": "2026-04-01 09:00",
          "players": 4
        }
      },
      "read": {
        "endpoint": "/api/bookings"
      },
      "delete": {
        "endpoint": "/api/bookings/{id}"
      }
    }
  }
}
```

**Usage:**
```bash
python3 scripts/generate_tests.py --config config-golf-app.json
python3 test_community_crud.py
python3 test_bookings_crud.py
```

---

## E-commerce API

Typical REST API for online store.

**config-ecommerce.json:**
```json
{
  "service": {
    "name": "MyShop API",
    "api_base": "https://api.myshop.com/v1"
  },
  
  "auth": {
    "method": "header",
    "token_key": "Authorization",
    "token_prefix": "Bearer"
  },
  
  "test_account": {
    "email": "test@myshop.com",
    "password": "testpass123"
  },
  
  "features": {
    "products": {
      "name": "Products",
      "create": {
        "endpoint": "/products",
        "params": {
          "required": ["name", "price"],
          "optional": ["description", "stock", "category"]
        },
        "id_field": "id",
        "test_data": {
          "name": "[TEST] Sample Product",
          "price": 29.99,
          "stock": 100
        }
      },
      "read": {
        "endpoint": "/products",
        "detail_endpoint": "/products/{id}"
      },
      "update": {
        "endpoint": "/products/{id}",
        "method": "PATCH",
        "params": {
          "required": ["name"],
          "optional": ["price", "stock"]
        }
      },
      "delete": {
        "endpoint": "/products/{id}"
      }
    },
    
    "orders": {
      "name": "Orders",
      "create": {
        "endpoint": "/orders",
        "params": {
          "required": ["product_id", "quantity"],
          "optional": ["notes"]
        },
        "id_field": "order.id",
        "test_data": {
          "product_id": 1,
          "quantity": 2
        }
      },
      "read": {
        "endpoint": "/orders",
        "detail_endpoint": "/orders/{id}"
      },
      "delete": {
        "endpoint": "/orders/{id}"
      }
    }
  }
}
```

---

## Social Media API

API for social networking features.

**config-social.json:**
```json
{
  "service": {
    "name": "SocialNet API",
    "api_base": "https://api.socialnet.io"
  },
  
  "auth": {
    "method": "header",
    "token_key": "X-Auth-Token"
  },
  
  "test_account": {
    "email": "testuser@example.com",
    "password": "password123",
    "login_endpoint": "/auth/signin"
  },
  
  "features": {
    "posts": {
      "name": "Social Posts",
      "create": {
        "endpoint": "/posts",
        "params": {
          "required": ["text"],
          "optional": ["media", "tags"]
        },
        "id_field": "post.id",
        "test_data": {
          "text": "[Test] This is a test post. Please ignore.",
          "tags": ["test", "qa"]
        }
      },
      "read": {
        "endpoint": "/posts/feed",
        "detail_endpoint": "/posts/{id}"
      },
      "update": {
        "endpoint": "/posts/{id}",
        "params": {
          "required": ["text"]
        }
      },
      "delete": {
        "endpoint": "/posts/{id}"
      }
    },
    
    "comments": {
      "name": "Comments",
      "create": {
        "endpoint": "/posts/{post_id}/comments",
        "params": {
          "required": ["text"],
          "optional": []
        },
        "id_field": "comment.id",
        "test_data": {
          "text": "[Test] Sample comment"
        }
      },
      "read": {
        "endpoint": "/posts/{post_id}/comments"
      },
      "update": {
        "endpoint": "/comments/{id}",
        "params": {
          "required": ["text"]
        }
      },
      "delete": {
        "endpoint": "/comments/{id}"
      }
    }
  }
}
```

---

## SaaS Project Management

Project/task management API.

**config-pm.json:**
```json
{
  "service": {
    "name": "TaskManager Pro",
    "api_base": "https://api.taskmanager.pro"
  },
  
  "auth": {
    "method": "header",
    "token_key": "Authorization",
    "token_prefix": "Token"
  },
  
  "test_account": {
    "email": "qa@company.com",
    "password": "qa_password",
    "login_endpoint": "/api/login",
    "token_path": "data.access_token",
    "user_id_path": "data.user.id"
  },
  
  "features": {
    "projects": {
      "name": "Projects",
      "create": {
        "endpoint": "/api/projects",
        "params": {
          "required": ["name"],
          "optional": ["description", "deadline"]
        },
        "id_field": "project.id",
        "test_data": {
          "name": "[QA Test] Sample Project",
          "description": "Auto-generated test project"
        }
      },
      "read": {
        "endpoint": "/api/projects",
        "detail_endpoint": "/api/projects/{id}"
      },
      "update": {
        "endpoint": "/api/projects/{id}",
        "method": "PATCH"
      },
      "delete": {
        "endpoint": "/api/projects/{id}"
      }
    },
    
    "tasks": {
      "name": "Tasks",
      "create": {
        "endpoint": "/api/tasks",
        "params": {
          "required": ["project_id", "title"],
          "optional": ["assignee", "priority", "due_date"]
        },
        "id_field": "task.id",
        "test_data": {
          "title": "[Test] Sample Task",
          "priority": "low"
        }
      },
      "read": {
        "endpoint": "/api/tasks",
        "detail_endpoint": "/api/tasks/{id}"
      },
      "update": {
        "endpoint": "/api/tasks/{id}",
        "method": "PATCH",
        "params": {
          "required": ["title"],
          "optional": ["status", "priority"]
        }
      },
      "delete": {
        "endpoint": "/api/tasks/{id}"
      }
    }
  },
  
  "response": {
    "success_codes": [200, 201, 204],
    "success_field": "success",
    "error_field": "error.message"
  }
}
```

---

## Minimal Example

Simplest possible configuration.

**config-minimal.json:**
```json
{
  "service": {
    "api_base": "https://api.example.com"
  },
  "test_account": {
    "email": "test@example.com",
    "password": "password"
  },
  "features": {
    "users": {
      "create": {
        "endpoint": "/users",
        "params": {
          "required": ["name", "email"]
        },
        "id_field": "id",
        "test_data": {
          "name": "Test User",
          "email": "testuser@example.com"
        }
      },
      "delete": {
        "endpoint": "/users/{id}"
      }
    }
  }
}
```

This generates a minimal Create→Delete transaction test.
