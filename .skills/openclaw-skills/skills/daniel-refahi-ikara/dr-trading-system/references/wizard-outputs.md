# Wizard Outputs

Wizard v1 should generate local deployment files such as:
- provider config
- watchlist configs
- job configs
- report template selection
- runtime state scaffold
- report folders
- optional schedule plan

## Keep local
The wizard should create these locally in the workspace:
- deployment/provider.yml
- deployment/watchlists/*.yml
- deployment/jobs/*.yml
- deployment/state/<job_id>/...
- deployment/reports/<job_id>/...
- deployment/schedules/ (optional)

## Do not generate in the skill package
Do not place generated deployment files under the reusable skill folder.
