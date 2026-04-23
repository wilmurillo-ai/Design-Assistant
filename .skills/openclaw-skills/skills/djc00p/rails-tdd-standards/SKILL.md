---
name: rails-tdd-standards
description: RSpec testing standards and best practices for Rails applications. Use when writing new tests, reviewing test quality, debugging factory errors, setting up FactoryBot, or enforcing single-expectation patterns. Also use when a test fails due to factory misconfiguration, wrong association keys, or missing role traits. Triggers on phrases like "write a test", "add specs", "factory error", "test is failing", "how should I test this", or when reviewing test code in a Rails project.
metadata: {"clawdbot":{"emoji":"🧪","requires":{"bins":["bundle"]},"os":["linux","darwin","win32"]}}
---

# Rails TDD Standards

Best practices for writing clean, reliable RSpec tests in Rails applications.

## Core Principle: Single Expectation

One assertion per test. Tests should read like specifications — each `it` block verifies exactly one thing.

```ruby
# ✅ Correct
it { is_expected.to validate_presence_of(:email) }
it { is_expected.to belong_to(:user) }

# ❌ Wrong — too many expectations in one test
it "validates the user" do
  expect(user).to validate_presence_of(:email)
  expect(user).to validate_presence_of(:name)
  expect(user).to be_valid
end
```

## FactoryBot Patterns

### Always use role traits
```ruby
# ✅ Correct
create(:user, :admin)
create(:user, :driver)
create(:user, :patron)

# ❌ Wrong — missing role context
create(:user)
```

### Association keys matter
Check your factory definitions carefully. Wrong keys cause silent failures.

```ruby
# ✅ Example — if your factory uses owner:
create(:profile, owner: user)

# ❌ Wrong key
create(:profile, user: user)  # fails if factory expects owner:
```

### Always set required associations
When a model requires a specific association to be valid, always set it explicitly — don't rely on factory defaults when they might be nil or wrong.

```ruby
# ✅ Explicit — clear intent, no surprises
let(:record) do
  create(:model, required_association: other_record)
end

# ❌ Implicit — may break if factory default changes
let(:record) { create(:model) }
```

### Use `described_class` not hardcoded class names
```ruby
# ✅
subject { described_class.new(params) }

# ❌
subject { MyService.new(params) }
```

## Common FactoryBot Gotchas

### Join tables without primary key
Tables with `id: false` can't use `.last` or `.first`.

```ruby
# ✅ Use a scoped query
record = JoinModel.find_by(field_a: a, field_b: b)

# ❌ Will raise ActiveRecord::MissingRequiredOrderError
record = JoinModel.last
```

### RecordInvalid from missing role/trait
If you see `Validation failed: X must have Y role` — you're missing a trait on the user factory.

```ruby
# ✅
user = create(:user, :driver)

# ❌ causes "must be a driver" validation error
user = create(:user)
```

## Spec Structure

```ruby
RSpec.describe MyClass do
  # Subject
  subject(:instance) { described_class.new(params) }

  # Shared setup
  let(:user) { create(:user, :admin) }

  # Group by behavior
  describe "#method_name" do
    context "when condition is true" do
      it "does the expected thing" do
        expect(instance.method_name).to eq(expected)
      end
    end

    context "when condition is false" do
      it "does something else" do
        expect(instance.method_name).to be_nil
      end
    end
  end
end
```

## Mocking & Stubbing

```ruby
# Stub a method
allow(object).to receive(:method_name).and_return(value)

# Stub and verify it was called
expect(object).to receive(:method_name).once

# Stub HTTP calls (WebMock)
stub_request(:post, "https://api.example.com/endpoint")
  .to_return(status: 200, body: { result: "ok" }.to_json)

# Allow localhost for system tests (if using WebMock)
WebMock.disable_net_connect!(allow_localhost: true)
```

## Service Object Testing

```ruby
RSpec.describe MyService do
  describe "#call" do
    context "with valid params" do
      it "returns the expected result" do
        result = described_class.new(valid_params).call
        expect(result).to be_a(ExpectedClass)
      end

      it "creates the expected record" do
        expect { described_class.new(valid_params).call }
          .to change(Record, :count).by(1)
      end
    end

    context "with invalid params" do
      it "returns false" do
        expect(described_class.new(invalid_params).call).to be(false)
      end
    end
  end
end
```

## Running Tests

```bash
# Run full suite
bundle exec rspec

# Run specific file
bundle exec rspec spec/models/user_spec.rb

# Run specific line
bundle exec rspec spec/models/user_spec.rb:42

# Run only failures from last run
bundle exec rspec --only-failures

# Run with documentation format
bundle exec rspec --format documentation
```

## See Also

- `references/factory-patterns.md` — advanced FactoryBot patterns
- `references/system-specs.md` — Capybara / browser testing setup
