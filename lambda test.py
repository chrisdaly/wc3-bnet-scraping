import lambda_function

event = {'queryStringParameters': {'server': 'azeroth', 'player': 'WEAREFOALS'}}
context = None
data = lambda_function.lambda_handler(event, context)
print(data)
