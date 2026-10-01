package todo.core

class TodosSuite extends munit.FunSuite:
  private def sample: List[Todo] =
    Todos.add(Nil, "Buy milk").toOption.get._2

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

  test("markDone sets done and is idempotent") {
    val list = sample
    val once = Todos.markDone(list, 1).toOption.get
    assertEquals(once.head.done, true)
    assertEquals(Todos.markDone(once, 1), Right(once))
  }

  test("edit replaces title under the same validation") {
    val list = sample
    val edited = Todos.edit(list, 1, Some("Buy oat milk")).toOption.get
    assertEquals(edited.head.title.value, "Buy oat milk")
    assertEquals(Todos.edit(list, 1, Some("  ")), Left(Todos.Error.InvalidTitle(Title.Error.Blank)))
  }

  test("remove deletes by id") {
    val list = sample
    assertEquals(Todos.remove(list, 1), Right(Nil))
  }

  test("unknown id fails for done/edit/remove") {
    assertEquals(Todos.markDone(Nil, 9), Left(Todos.Error.UnknownId(9)))
    assertEquals(Todos.edit(Nil, 9, Some("x")), Left(Todos.Error.UnknownId(9)))
    assertEquals(Todos.remove(Nil, 9), Left(Todos.Error.UnknownId(9)))
  }

  test("add with planning metadata and filter by tag") {
    val meta = Todos.Meta(
      due = Some("2026-10-01"),
      priority = Some("high"),
      tags = Some(List("work")),
      assignees = Some(List("a@example.com")),
      assigner = Some("b@example.com")
    )
    val (_, list) = Todos.add(Nil, "Ship it", meta).toOption.get
    assertEquals(list.head.due.map(_.value.toString), Some("2026-10-01"))
    assertEquals(list.head.priority.map(Priority.render), Some("high"))
    val filtered = Todos.filter(list, tag = Some("work")).toOption.get
    assertEquals(filtered.length, 1)
    assertEquals(Todos.filter(list, tag = Some("home")).toOption.get, Nil)
  }
