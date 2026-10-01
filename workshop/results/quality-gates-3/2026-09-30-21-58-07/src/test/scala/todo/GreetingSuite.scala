package todo

class GreetingSuite extends munit.FunSuite:
  test("the greeting is a non-blank pure value") {
    assert(Greeting.message.trim.nonEmpty)
  }
