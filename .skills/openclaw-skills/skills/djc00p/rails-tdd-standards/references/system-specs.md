# System Specs (Capybara / Browser Testing)

## Setup

System specs require a browser driver. Common options:

**Firefox + geckodriver:**
```bash
# Install geckodriver
wget https://github.com/mozilla/geckodriver/releases/download/v0.36.0/geckodriver-v0.36.0-linux64.tar.gz
tar -xz -C ~/.local/bin -f geckodriver*.tar.gz
```

**Chrome + chromedriver:**
```bash
# Ubuntu
sudo apt install chromium-browser chromium-chromedriver
```

**rails_helper.rb config:**
```ruby
config.before(type: :system) do
  driven_by :selenium_firefox_headless
  # or: driven_by :selenium_chrome_headless
end
```

## WebMock Conflict

If you use WebMock for HTTP stubbing, system specs may fail because WebMock blocks localhost connections that Capybara needs.

Fix:
```ruby
# spec/rails_helper.rb or spec/support/webmock.rb
WebMock.disable_net_connect!(allow_localhost: true)
```

## Writing System Specs

```ruby
RSpec.describe "User sign in", type: :system do
  let(:user) { create(:user, :confirmed, password: "password123") }

  it "signs in successfully" do
    visit sign_in_path
    fill_in "Email", with: user.email
    fill_in "Password", with: "password123"
    click_button "Sign in"
    expect(page).to have_text("Welcome back")
  end
end
```

## Common Capybara Methods

```ruby
visit path                          # navigate to URL
click_link "text"                   # click a link by text
click_button "text"                 # click a button
fill_in "Label", with: "value"      # fill in a form field
select "option", from: "Label"      # select from dropdown
check "Label"                       # check a checkbox
within("css-selector") { ... }      # scope interactions
expect(page).to have_text("...")    # assert text on page
expect(page).to have_css(".class")  # assert element present
expect(current_path).to eq(path)    # assert URL
```

## Turbo / Modal Interactions

When content loads inside a Turbo frame:
```ruby
within("turbo-frame#modal") do
  fill_in "Email", with: "user@example.com"
  click_button "Submit"
end
```

## Performance Tips

- System specs are slow (browser startup) — use them sparingly
- Prefer request specs for controller/API behavior
- Use system specs only for full user flows that require JS
- Run system specs separately if they're slowing your suite: `bundle exec rspec spec/system`
