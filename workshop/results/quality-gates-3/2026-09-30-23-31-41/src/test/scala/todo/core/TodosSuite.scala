package todo.core

class TodosSuite extends munit.FunSuite:
  test("adding to an empty list creates a not-done todo with id 1") {
    Todos.add(Nil, "Buy milk") match
      case Right((created, updated)) =>
        assertEquals(created.id.value, 1)
        assertEquals(created.title.value, "Buy milk")
        assertEquals(created.done, false)
        assertEquals(updated, List(created))
      case Left(err) => fail(s"expected success, got $err")
  }

  test("adding to a non-empty list assigns the next unused id") {
    val (first, afterFirst) = Todos.add(Nil, "Buy milk").toOption.get
    Todos.add(afterFirst, "Walk dog") match
      case Right((second, afterSecond)) =>
        assertEquals(second.id.value, 2)
        assertEquals(afterSecond, List(first, second))
      case Left(err) => fail(s"expected success, got $err")
  }

  test("adding a blank title fails instead of appending anything") {
    assertEquals(Todos.add(Nil, "   "), Left(Todos.Error.InvalidTitle(Title.Error.Blank)))
  }
