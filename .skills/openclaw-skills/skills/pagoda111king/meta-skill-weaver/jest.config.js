module.exports = {
  testEnvironment: 'node',
  testMatch: ['**/tests/**/*.test.js'],
  collectCoverageFrom: [
    'src/event-bus.js',
    'src/first-principle-decomposer.js',
    'src/middleware-chain.js',
    'src/state-machine.js',
    'src/state-persistence.js',
    'src/state-persistence-middleware.js'
  ],
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov', 'html'],
  coverageThreshold: {
    global: {
      branches: 50,
      functions: 60,
      lines: 60,
      statements: 60
    }
  },
  verbose: true,
  testTimeout: 10000
};
