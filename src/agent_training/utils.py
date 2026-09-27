class Utils:
    def calculate_average(self, numbers: list[int]) ->float:
        return sum(numbers)/len(numbers)
    def greet(self, name: str) ->str:
        return f"Hello, {name}!"   