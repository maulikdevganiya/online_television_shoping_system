# TODO: Make Admin Dashboard Dynamic

## Steps to Complete

- [ ] Update dashboard view in customadmin/views.py to fetch dynamic data:

  - [ ] Calculate total revenue from completed payments
  - [ ] Count total orders
  - [ ] Count pending orders (as inquiries)
  - [ ] Count total customers
  - [ ] Fetch recent 3 orders with details
  - [ ] Calculate monthly revenue for current year
  - [ ] Calculate sales by brand category

- [ ] Modify customadmin/templates/dashboard.html:

  - [ ] Replace hardcoded statistics with Django template variables
  - [ ] Pass chart data to JavaScript for dynamic rendering

- [x] Test the dashboard to ensure data loads correctly
- [x] Verify calculations match expected values
