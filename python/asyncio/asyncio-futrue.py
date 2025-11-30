from asyncio import Future

my_future = Future()

print(f"Is my future done? {my_future.done()}")

# my_future.set_result(23)
my_future.set_exception(Exception("oops!"))
print(f"Is my future done? {my_future.done()}")
try:
  print(f"result: {my_future.result()}")
except Exception as e:
  print("something error ocurred:", e)

