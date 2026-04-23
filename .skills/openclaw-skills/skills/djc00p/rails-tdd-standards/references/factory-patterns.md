# FactoryBot Advanced Patterns

## Traits

Traits let you define variations of a factory cleanly.

```ruby
FactoryBot.define do
  factory :user do
    first_name { "John" }
    last_name  { "Doe" }
    email      { Faker::Internet.email }

    trait :admin do
      after(:create) { |u| u.add_role(:admin) }
    end

    trait :driver do
      after(:create) { |u| u.add_role(:driver) }
    end

    trait :confirmed do
      confirmed_at { Time.current }
    end
  end
end
```

Usage:
```ruby
create(:user, :admin, :confirmed)
create(:user, :driver)
```

## Associations

```ruby
FactoryBot.define do
  factory :post do
    title { "Sample Post" }
    association :author, factory: :user  # explicit factory name
  end
end
```

Or in tests:
```ruby
let(:user) { create(:user) }
let(:post) { create(:post, author: user) }  # pass the instance
```

## build vs create

```ruby
build(:user)    # instantiates but doesn't save — fast, no DB hit
create(:user)   # saves to DB — use when you need an id or associations
build_stubbed(:user)  # fake record with id, no DB — fastest
```

Prefer `build` or `build_stubbed` for unit tests where persistence isn't needed.

## Sequences

Ensure unique values across tests:

```ruby
sequence(:email) { |n| "user#{n}@example.com" }
sequence(:phone) { |n| "+1303555#{n.to_s.rjust(4, '0')}" }

factory :user do
  email { generate(:email) }
  phone_number { generate(:phone) }
end
```

## Callbacks

```ruby
factory :driver_profile do
  after(:create) do |profile|
    create(:vehicle, owner: profile)  # always create a vehicle for driver profiles
  end
end
```

Use sparingly — callbacks make factories harder to reason about.

## Nested Associations

```ruby
# ✅ Build the chain explicitly in tests for clarity
let(:user)    { create(:user, :driver) }
let(:business) { create(:business_profile, owner: user) }
let(:profile) { create(:driver_profile, user: user, business_profile: business) }
let(:vehicle) { create(:vehicle, business_profile: business, primary_driver: profile) }
```

This is more verbose but makes the setup obvious and debuggable.
