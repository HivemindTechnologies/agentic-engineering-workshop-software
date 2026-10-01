package todo.render

import todo.core.{Title, Todo, TodoId}

class RendererSuite extends munit.FunSuite:
  private def todo(id: Int, title: String, done: Boolean): Todo =
    Todo(TodoId(id), Title(title).getOrElse(fail("expected a valid title")), done)

  test("an empty list renders the no-todos message") {
    assertEquals(Renderer.renderList(Nil), "No todos yet.")
  }

  test("a non-empty list renders one line per todo naming id, title and done state") {
    val rendered = Renderer.renderList(
      List(todo(1, "Buy milk", done = false), todo(2, "Walk dog", done = true))
    )
    val lines = rendered.linesIterator.toList
    assertEquals(lines.length, 2)
    assert(lines(0).contains("1") && lines(0).contains("Buy milk") && lines(0).contains("pending"))
    assert(lines(1).contains("2") && lines(1).contains("Walk dog") && lines(1).contains("done"))
  }
