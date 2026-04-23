class MockDB {
  constructor() {
    this.data = {
      users: [],
      agents: [],
      tasks: []
    };
    this.lastId = { users: 0, agents: 0, tasks: 0 };
  }

  prepare(sql) {
    const self = this;
    let queryInfo = { sql, params: [] };

    return {
      run: function(...params) {
        queryInfo.params = params;
        
        if (sql.includes('INSERT INTO users')) {
          const userData = {};
          if (sql.includes('username = ?')) userData.username = params[0];
          if (sql.includes('email = ?')) userData.email = params[1];
          if (sql.includes('password = ?')) userData.password = params[2];
          if (sql.includes('role = ?')) userData.role = params[3];
          if (sql.includes('status = ?')) userData.status = params[4];
          
          self.lastId.users++;
          userData.id = self.lastId.users;
          userData.created_at = new Date().toISOString();
          userData.updated_at = new Date().toISOString();
          self.data.users.push(userData);
          return { lastInsertRowid: userData.id, changes: 1 };
        }
        
        if (sql.includes('INSERT INTO agents')) {
          const agentData = {};
          if (sql.includes('name = ?')) agentData.name = params[0];
          if (sql.includes('status = ?')) agentData.status = params[1];
          if (sql.includes('current_task_id = ?')) agentData.current_task_id = params[2];
          if (sql.includes('last_heartbeat = ?')) agentData.last_heartbeat = params[3];
          if (sql.includes('ip_address = ?')) agentData.ip_address = params[4];
          if (sql.includes('address = ?')) agentData.address = params[5];
          if (sql.includes('role = ?')) agentData.role = params[6];
          if (sql.includes('version = ?')) agentData.version = params[7];
          
          self.lastId.agents++;
          agentData.id = self.lastId.agents;
          agentData.created_at = new Date().toISOString();
          agentData.updated_at = new Date().toISOString();
          self.data.agents.push(agentData);
          return { lastInsertRowid: agentData.id, changes: 1 };
        }
        
        if (sql.includes('INSERT INTO tasks')) {
          const taskData = {};
          if (sql.includes('title = ?')) taskData.title = params[0];
          if (sql.includes('description = ?')) taskData.description = params[1];
          if (sql.includes('priority = ?')) taskData.priority = params[2];
          if (sql.includes('status = ?')) taskData.status = params[3];
          if (sql.includes('assignee_id = ?')) taskData.assignee_id = params[4];
          if (sql.includes('created_at = ?')) taskData.created_at = params[5];
          if (sql.includes('updated_at = ?')) taskData.updated_at = params[6];
          
          self.lastId.tasks++;
          taskData.id = self.lastId.tasks;
          self.data.tasks.push(taskData);
          return { lastInsertRowid: taskData.id, changes: 1 };
        }
        
        if (sql.includes('UPDATE')) {
          const tableMatch = sql.match(/UPDATE (\w+)/);
          const table = tableMatch ? tableMatch[1] : 'users';
          
          if (sql.includes('WHERE id = ?')) {
            const id = params[params.length - 1];
            const updateData = {};
            
            const statusMatch = sql.match(/status = ['"]([^'"]+)['"]/);
            if (statusMatch) {
              updateData.status = statusMatch[1];
            }
            
            const fields = [];
            if (sql.includes('email = ?')) fields.push('email');
            if (sql.includes('password = ?')) fields.push('password');
            if (sql.includes('status = ?')) fields.push('status');
            if (sql.includes('name = ?')) fields.push('name');
            if (sql.includes('last_heartbeat = ?')) fields.push('last_heartbeat');
            if (sql.includes('current_task_id = ?')) fields.push('current_task_id');
            if (sql.includes('assignee_id = ?')) fields.push('assignee_id');
            if (sql.includes('title = ?')) fields.push('title');
            
            let paramIndex = 0;
            if (fields.includes('email')) updateData.email = params[paramIndex++];
            if (fields.includes('password')) updateData.password = params[paramIndex++];
            if (fields.includes('status') && !updateData.status) updateData.status = params[paramIndex++];
            if (fields.includes('name')) updateData.name = params[paramIndex++];
            if (fields.includes('last_heartbeat')) updateData.last_heartbeat = params[paramIndex++];
            if (fields.includes('current_task_id')) updateData.current_task_id = params[paramIndex++];
            if (fields.includes('assignee_id')) updateData.assignee_id = params[paramIndex++];
            if (fields.includes('title')) updateData.title = params[paramIndex++];
            
            const index = self.data[table].findIndex(item => item.id === id);
            if (index !== -1) {
              self.data[table][index] = { ...self.data[table][index], ...updateData };
              return { changes: 1 };
            }
            return { changes: 0 };
          }
          return { changes: 0 };
        }
        
        if (sql.includes('DELETE')) {
          const tableMatch = sql.match(/DELETE FROM (\w+)/);
          const table = tableMatch ? tableMatch[1] : 'users';
          
          if (sql.includes('WHERE id = ?')) {
            const id = params[0];
            const initialLength = self.data[table].length;
            self.data[table] = self.data[table].filter(item => item.id !== id);
            return { changes: initialLength - self.data[table].length };
          }
          return { changes: 0 };
        }
        
        return { changes: 0 };
      },
      
      get: function(...params) {
        queryInfo.params = params;
        const tableMatch = sql.match(/SELECT \* FROM (\w+)/);
        const table = tableMatch ? tableMatch[1] : 'users';
        
        if (sql.includes('WHERE id = ?')) {
          const id = params[0];
          const result = self.data[table].find(item => item.id === id);
          return result || null;
        }
        
        if (sql.includes('WHERE email = ?')) {
          const email = params[0];
          return self.data[table].find(item => item.email === email) || null;
        }
        
        if (sql.includes('WHERE username = ?')) {
          const username = params[0];
          return self.data[table].find(item => item.username === username) || null;
        }
        
        if (sql.includes('WHERE name = ?')) {
          const name = params[0];
          return self.data[table].find(item => item.name === name) || null;
        }
        
        if (sql.includes('WHERE status = ?')) {
          const status = params[0];
          return self.data[table].find(item => item.status === status) || null;
        }
        
        if (sql.includes('SELECT * FROM tasks') && !sql.includes('WHERE')) {
          return [...self.data.tasks];
        }
        
        if (sql.includes('COUNT(*)')) {
          let count = self.data[table].length;
          
          if (sql.includes("WHERE status = 'pending'") && !sql.includes('AND')) {
            count = self.data[table].filter(item => item.status === 'pending').length;
          } else if (sql.includes("WHERE status = 'in_progress'") && !sql.includes('AND')) {
            count = self.data[table].filter(item => item.status === 'in_progress').length;
          } else if (sql.includes("WHERE status = 'completed'") && !sql.includes('AND')) {
            count = self.data[table].filter(item => item.status === 'completed').length;
          } else if (sql.includes("WHERE status = 'idle'") && !sql.includes('AND')) {
            count = self.data[table].filter(item => item.status === 'idle').length;
          } else if (sql.includes("WHERE status = 'busy'") && !sql.includes('AND')) {
            count = self.data[table].filter(item => item.status === 'busy').length;
          } else if (sql.includes('WHERE status = ?')) {
            const status = params[0];
            count = self.data[table].filter(item => item.status === status).length;
          } else if (!sql.includes('WHERE')) {
            count = self.data[table].length;
          } else {
            count = self.data[table].length;
          }
          
          return { count: count };
        }
        
        if (sql.includes('COUNT(*)') && sql.includes('WHERE status = "pending"')) {
          return { count: self.data[table].filter(item => item.status === 'pending').length };
        }
        if (sql.includes('COUNT(*)') && sql.includes('WHERE status = "in_progress"')) {
          return { count: self.data[table].filter(item => item.status === 'in_progress').length };
        }
        if (sql.includes('COUNT(*)') && sql.includes('WHERE status = "completed"')) {
          return { count: self.data[table].filter(item => item.status === 'completed').length };
        }
        
        if (sql.includes('SUM(CASE')) {
          const total = self.data[table].length;
          const pending = self.data[table].filter(t => t.status === 'pending').length;
          const inProgress = self.data[table].filter(t => t.status === 'in_progress').length;
          const completed = self.data[table].filter(t => t.status === 'completed').length;
          return { total, pending, in_progress: inProgress, completed };
        }
        
        return null;
      },
      
      all: function(...params) {
        queryInfo.params = params;
        const tableMatch = sql.match(/SELECT \* FROM (\w+)/);
        const table = tableMatch ? tableMatch[1] : 'users';
        
        let results = [...self.data[table]];
        
        if (sql.includes("WHERE status = 'pending' AND assignee_id IS NULL")) {
          results = results.filter(item => item.status === 'pending' && (item.assignee_id === null || item.assignee_id === undefined));
        }
        else if (sql.includes("WHERE status = 'idle'")) {
          results = results.filter(item => item.status === 'idle');
        }
        else if (sql.includes("WHERE status = 'busy'")) {
          results = results.filter(item => item.status === 'busy');
        }
        else if (sql.includes("WHERE status = 'pending'") && !sql.includes('AND')) {
          results = results.filter(item => item.status === 'pending');
        }
        else if (sql.includes("WHERE status = 'in_progress'") && !sql.includes('AND')) {
          results = results.filter(item => item.status === 'in_progress');
        }
        else if (sql.includes("WHERE status = 'completed'") && !sql.includes('AND')) {
          results = results.filter(item => item.status === 'completed');
        }
        else if (sql.includes('WHERE status = ?')) {
          const status = params[0];
          results = results.filter(item => item.status === status);
        }
        else if (sql.includes('WHERE assignee_id = ?')) {
          const assigneeId = params[0];
          results = results.filter(item => item.assignee_id === assigneeId);
        }
        else if (sql.includes('WHERE assignee_id IS NULL')) {
          results = results.filter(item => item.assignee_id === null || item.assignee_id === undefined);
        }
        else if (sql.includes('WHERE status = ?') && sql.includes('AND assignee_id IS NULL')) {
          const status = params[0];
          results = results.filter(item => item.status === status && (item.assignee_id === null || item.assignee_id === undefined));
        }
        
        return results;
      }
    };
  }
}

// 测试
const mockDB = new MockDB();

// 模拟插入任务
mockDB.data.tasks = [
  { id: 1, title: 'Task 1', description: 'Desc 1', priority: 1, status: 'pending', assignee_id: null, created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
  { id: 2, title: 'Task 2', description: 'Desc 2', priority: 2, status: 'in_progress', assignee_id: 1, created_at: new Date().toISOString(), updated_at: new Date().toISOString() }
];

const sql = "SELECT * FROM tasks WHERE status = 'pending' AND assignee_id IS NULL";
console.log('SQL:', sql);
console.log('Tasks:', mockDB.data.tasks);

const result = mockDB.prepare(sql).all();
console.log('Result:', result);
console.log('Length:', result.length);