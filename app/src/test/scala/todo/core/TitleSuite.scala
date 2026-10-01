package todo.core

class TitleSuite extends munit.FunSuite:
  test("a non-blank title is accepted") {
    assertEquals(Title("Buy milk").map(_.value), Right("Buy milk"))
  }

  test("a blank title is rejected, not silently accepted") {
    assertEquals(Title(""), Left(Title.Error.Blank))
  }

  test("a whitespace-only title is rejected, never silently trimmed to empty") {
    assertEquals(Title("   "), Left(Title.Error.Blank))
  }
