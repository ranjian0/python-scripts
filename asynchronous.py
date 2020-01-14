import asyncio

def is_prime(x):
    return not any(x//i == x/i for i in range(x-1, 1, -1))
    
async def highest_prime_below(x):
    print(f"highest prime below {x}")
    
    for y in range(x-1, 0, -1):
        if is_prime(y):
            print(f" -> highest prime below {x} is {y}")
            return y
        await asyncio.sleep(0.000001)
    return None
    
async def main():
    await asyncio.wait([
        highest_prime_below(100000),
        highest_prime_below(1000),
        highest_prime_below(100)
    ])
    
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
