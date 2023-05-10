from aiohttp import web
import redis
import json

# Redis connection
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Conversion, on this example 1 dollar = 76 rubles
RUB_TO_USD = 76

# GET /convert?from=RUR&to=USD&amount=42
async def convert(request):
    params = request.rel_url.query
    from_currency = params.get('from')
    to_currency = params.get('to')
    amount = float(params.get('amount'))

    if from_currency == 'RUR' and to_currency == 'USD':
        converted_amount = amount / RUB_TO_USD
        response = {
            'from': from_currency,
            'to': to_currency,
            'amount': amount,
            'converted_amount': converted_amount
        }
        return web.Response(text=json.dumps(response), content_type='application/json')
    else:
        return web.Response(text='Conversion not supported', status=400)


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
    web.run_app(app)