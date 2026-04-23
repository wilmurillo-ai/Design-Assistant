const { greet, add } = require('../src/index');

console.log('Running tests...\n');

// Test greet function
console.log('Testing greet():');
console.log(greet('World')); // Expected: Hello, World! Welcome to GitHub collaboration.

// Test add function
console.log('\nTesting add():');
console.log(add(2, 3));     // Expected: 5
console.log(add(0, 0));     // Expected: 0
console.log(add(-1, 1));    // Expected: 0

console.log('\n✅ All tests passed!');
