from aiohttp import web
import redis
import json

# Redis connection
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# GET /convert?from=RUR&to=USD&amount=42
async def convert(request):
    from_currency = request.query.get('from') #RUR
    to_currency = request.query.get('to') #USD
    amount = float(request.query.get('amount'))

    # Query Redis to get exchange rate for the given currencies
    exchange_rate = redis_client.get(f'{from_currency}:{to_currency}') #The key format is Currency1:Currency2
    if exchange_rate is None:
        return web.Response(status=400, text='Exchange rate not found')

    else:
        # Calculate the converted amount
        converted_amount = amount * float(exchange_rate)

        # Return the result as JSON
        return web.json_response({
            'from_currency': from_currency,
            'to_currency': to_currency,
            'amount': amount,
            'converted_amount': converted_amount
        })


# POST /database?merge=1
async def database(request):
    params = request.rel_url.query
    merge = params.get('merge')

    if merge == '0':
        # Disable old data
        response = {'message': 'Old data disabled'}
    elif merge == '1':
        # Set new data
        data = await request.json()
        redis_client.set('currency_data', json.dumps(data))
        response = {'message': 'New data set'}
    else:
        return web.Response(text='Invalid merge parameter', status=400)

    return web.Response(text=json.dumps(response), content_type='application/json')


app = web.Application()
app.router.add_get('/convert', convert)
app.router.add_post('/database', database)

if __name__ == '__main__':
    print(redis_client.get("RUR:USD"))
    web.run_app(app)