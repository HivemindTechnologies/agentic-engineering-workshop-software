package todo.render

import todo.core.{Priority, Todo}
import todo.store.Store

object Renderer:
  private val NoTodosMessage = "No todos yet."
  private val Esc = '\u001b'

  def noTodosMessage: String = NoTodosMessage

  def renderTable(todos: List[Todo], color: Boolean): String =
    if todos.isEmpty then NoTodosMessage
    else
      val rows = todos.map(tableCells)
      val headers = List("ID", "STATE", "TITLE", "DUE", "PRI", "TAGS", "ASSIGNEE", "ASSIGNER")
      val widths = headers.indices.map { i =>
        (headers(i).length :: rows.map(_(i).length)).max
      }.toList
      val headerLine = formatRow(headers, widths)
      val body = rows.map { cells =>
        val plain = formatRow(cells, widths)
        if color then colorize(plain, cells(1) == "[x]") else plain
      }
      (headerLine :: body).mkString("\n")

  def renderYaml(todos: List[Todo]): String =
    Store.encode(todos).trim

  def renderJson(todos: List[Todo]): String =
    if todos.isEmpty then "[]"
    else todos.map(jsonOne).mkString("[", ",", "]")

  def renderMarkdown(todos: List[Todo]): String =
    val header =
      "| ID | STATE | TITLE | DUE | PRI | TAGS | ASSIGNEE | ASSIGNER |\n| --- | --- | --- | --- | --- | --- | --- | --- |"
    if todos.isEmpty then header
    else
      val rows = todos.map { t =>
        val state = if t.done then "done" else "pending"
        s"| ${t.id.value} | $state | ${t.title.value} | ${due(t)} | ${pri(t)} | ${tags(t)} | ${assignees(t)} | ${assigner(t)} |"
      }
      (header :: rows).mkString("\n")

  def stripAnsi(text: String): String =
    text.replaceAll(s"$Esc\\[[0-9;]*m", "")

  private def tableCells(todo: Todo): List[String] =
    List(
      todo.id.value.toString,
      if todo.done then "[x]" else "[ ]",
      todo.title.value,
      due(todo),
      pri(todo),
      tags(todo),
      assignees(todo),
      assigner(todo)
    )

  private def due(t: Todo): String = t.due.map(_.value.toString).getOrElse("")
  private def pri(t: Todo): String = t.priority.map(Priority.render).getOrElse("")
  private def tags(t: Todo): String = t.tags.map(_.value).mkString(",")
  private def assignees(t: Todo): String = t.assignees.map(_.value).mkString(",")
  private def assigner(t: Todo): String = t.assigner.map(_.value).getOrElse("")

  private def jsonOne(t: Todo): String =
    val parts = List(
      s""""id":${t.id.value}""",
      s""""title":"${escapeJson(t.title.value)}"""",
      s""""done":${t.done}"""
    ) ++
      t.due.map(d => s""""due":"${d.value}"""").toList ++
      t.priority.map(p => s""""priority":"${Priority.render(p)}"""").toList ++
      List(
        s""""tags":[${t.tags.map(x => s""""${escapeJson(x.value)}"""").mkString(",")}]""",
        s""""assignees":[${t.assignees.map(x => s""""${escapeJson(x.value)}"""").mkString(",")}]"""
      ) ++
      t.assigner.map(a => s""""assigner":"${escapeJson(a.value)}"""").toList
    parts.mkString("{", ",", "}")

  private def formatRow(cells: List[String], widths: List[Int]): String =
    cells.zip(widths).map { case (c, w) => c.padTo(w, ' ') }.mkString("  ")

  private def colorize(plain: String, done: Boolean): String =
    val code = if done then "32" else "37"
    s"$Esc[${code}m$plain$Esc[0m"

  private def escapeJson(s: String): String =
    s.flatMap {
      case '"'  => "\\\""
      case '\\' => "\\\\"
      case '\n' => "\\n"
      case '\r' => "\\r"
      case '\t' => "\\t"
      case c    => c.toString
    }
