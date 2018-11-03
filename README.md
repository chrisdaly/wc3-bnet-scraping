# wc3-bnet-scraping
Scrapes a player's profile and returns JSON. Utilized with AWS API Gateway as the Lambda function.

## TODO
Scrape everything on the page.
Replace "rank": null with N/A.
Keep only numbers, let downstream format to string etc. Check what twitter does here.
More defined endpoints.
Start incorporating twitch bot.
(SQS?)
Figure out how to propogate errors from internal to response.