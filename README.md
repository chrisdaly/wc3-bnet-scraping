# wc3-bnet-scraping
Scrapes a player's profile and returns JSON. Utilized with AWS API Gateway as the Lambda function.

## Example
https://bqeat6w63f.execute-api.us-east-1.amazonaws.com/dev?server=northrend&player=WEAREFOALS

```
{
"individual": {
"random_team": {
"wins": 67,
"losses": 40,
"rank": null,
"experience": "6,930",
"level": 18.86,
"win_percentage": 62.62
}
},
"team": [
{
"wins": 96,
"losses": 7,
"partners": [
"KODOS_FORSAKEN."
],
"rank": 52,
"level": 29.96,
"win_percentage": 93.2
},
{
"wins": 1,
"losses": 0,
"partners": [
"MEG",
"rinne"
],
"rank": 346,
"level": 5.52,
"win_percentage": 100.0
},
{
"wins": 14,
"losses": 3,
"partners": [
"ENA1337"
],
"rank": 821,
"level": 13.1,
"win_percentage": 82.35
},
{
"wins": 4,
"losses": 1,
"partners": [
"ShoananasS"
],
"rank": null,
"level": 8.72,
"win_percentage": 80.0
},
{
"wins": 79,
"losses": 2,
"partners": [
"LongWalk"
],
"rank": 59,
"level": 28.6,
"win_percentage": 97.53
},
{
"wins": 1,
"losses": 0,
"partners": [
"MEG",
"protege"
],
"rank": 336,
"level": 5.6,
"win_percentage": 100.0
}
]
}
```


## TODO
- Scrape everything on the page.
- Replace "rank": null with N/A.
- Keep only numbers, let downstream format to string etc. Check what twitter does here.
- More defined endpoints.
- Start incorporating twitch bot.
- (SQS?)
- Figure out how to propogate errors from internal to response.
