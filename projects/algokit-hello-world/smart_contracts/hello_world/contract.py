from algopy import ARC4Contract, String, Box, Bytes
from algopy.arc4 import abimethod

class HelloWorld(ARC4Contract):
    def __init__(self) -> None:
        self.greeting_box = Box(String, key=Bytes(b"greeting"))
        self.initialized = Box(Bytes, key=Bytes(b"initialized"))

    @abimethod()
    def hello(self, name: String) -> String:
        greeting = String("Hello, ") + name
        self.greeting_box.value = greeting
        self.initialized.value = Bytes(b"1")
        return greeting

    @abimethod()
    def read_greeting(self) -> String:
        if self.initialized.value == Bytes(b"1"):
            return self.greeting_box.value
        return String("No greeting stored yet.")

    @abimethod()
    def is_initialized(self) -> Bytes:
        return self.initialized.value
