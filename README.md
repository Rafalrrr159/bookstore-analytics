TASK

Load data from DATA1 folder into pandas and clean it – ensure proper types, for example, make dates are parsed as dates, handle any duplicated, missing or malformed values.
Add a column paid_price = quantity * unit_price to orders (convert everything to dollars and cents, €1 = $1.2).
Extract date (year, month and day) from timestamp.
1. Compute daily revenue (sum of paid_price grouped by date) and find top 5 days by revenue.,
2. Find how many real unique users there are. Note that user can change address or change phone or even provide alias instead of a real name; you need to reconciliate data. You may assume that only one field is changed.,
3. Find how how many unique sets of authors there are. For example, if John and Paul wrote a book together and wrote several books separately, it means that there are 3 different sets.,
4. Find the most popular (by sold book count) author (or author set).,
5. Identify the top customer by total spending (list all user_id values for the possible different addresses, phones, e-mails, or aliases).,
6. Plot a simple line chart of daily revenue using matplotlib.,

Repeat for the data from DATA2 and DATA3 folders separately.

Make sure the information is presented neatly and professionally, resembling a BI dashboard rather than plain text.
Dashboard:
1. Top 5 days by revenue using the format "YYYY-MM-dd".
2. Number of unique users.
3. Number of unique sets of authors.
4. The name of most popular author(s).
5. Best buyer (with aliases) as an array of ids ([id1, id2, ...])
6. Daily revenue chart
