package todo.render

import org.virtuslab.yaml.*

import todo.core.{Email, Title, Todo, TodoId}
import todo.store.TodoRecord

class RendererSuite extends munit.FunSuite:
  private def todo(id: Int, title: String, done: Boolean): Todo =
    Todo(TodoId(id), Title(title).getOrElse(fail("expected a valid title")), done)

  test("empty list table renders the no-todos message") {
    assertEquals(Renderer.renderTable(Nil, color = false), "No todos yet.")
  }

  test("table has header and aligned columns with state markers") {
    val rendered = Renderer.renderTable(
      List(todo(1, "Buy milk", done = false), todo(100, "Walk the very long dog", done = true)),
      color = false
    )
    val lines = rendered.linesIterator.toList
    assert(
      lines.head.contains("ID") && lines.head.contains("STATE") && lines.head.contains("TITLE")
    )
    assert(lines(1).contains("[ ]") && lines(1).contains("Buy milk"))
    assert(lines(2).contains("[x]") && lines(2).contains("Walk the very long dog"))
    val id1 = lines(1).indexOf("1")
    val id100 = lines(2).indexOf("100")
    assertEquals(id1, id100)
  }

  test("color on embeds ANSI; color off does not") {
    val todos = List(todo(1, "A", done = false), todo(2, "B", done = true))
    val colored = Renderer.renderTable(todos, color = true)
    val plain = Renderer.renderTable(todos, color = false)
    assert(colored.contains("\u001b["))
    assert(!plain.contains("\u001b["))
    assertEquals(Renderer.stripAnsi(colored), plain)
  }

  test("yaml empty list is []") {
    assertEquals(Renderer.renderYaml(Nil), "[]")
  }

  test("yaml round-trips through the store schema") {
    val todos = List(todo(1, "Buy milk", done = false), todo(2, "Walk dog", done = true))
    val yaml = Renderer.renderYaml(todos)
    val decoded = yaml.as[List[TodoRecord]].getOrElse(fail("yaml decode failed"))
    assertEquals(
      decoded.map(r => (r.id, r.title, r.done)),
      List((1, "Buy milk", false), (2, "Walk dog", true))
    )
  }

  test("json empty is [] and fields are stable") {
    assertEquals(Renderer.renderJson(Nil), "[]")
    val json = Renderer.renderJson(List(todo(1, "Buy milk", done = false)))
    assert(json.contains("\"id\":1"))
    assert(json.contains("\"title\":\"Buy milk\""))
    assert(json.contains("\"done\":false"))
  }

  test("assigner is shown in table, markdown and json when set") {
    val boss = Email("boss@example.com").getOrElse(fail("expected a valid email"))
    val withAssigner = todo(1, "Review", done = false).copy(assigner = Some(boss))
    val table = Renderer.renderTable(List(withAssigner), color = false)
    assert(table.linesIterator.next().contains("ASSIGNER"))
    assert(table.contains("boss@example.com"))
    val md = Renderer.renderMarkdown(List(withAssigner))
    assert(md.contains("ASSIGNER") && md.contains("boss@example.com"))
    assert(Renderer.renderJson(List(withAssigner)).contains(""""assigner":"boss@example.com""""))
  }

  test("an unset assigner renders as an empty cell, not the word None") {
    val plain = todo(1, "Plain", done = false)
    assert(!Renderer.renderTable(List(plain), color = false).contains("None"))
    assert(!Renderer.renderMarkdown(List(plain)).contains("None"))
  }

  test("markdown is a pipe table without ANSI") {
    val md = Renderer.renderMarkdown(List(todo(1, "Buy milk", done = true)))
    assert(md.contains("| ID |"))
    assert(md.contains("Buy milk"))
    assert(!md.contains("\u001b["))
  }
