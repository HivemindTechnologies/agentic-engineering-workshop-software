package todo.render

import todo.core.Todo

/**
 * The M3 plain-text listing. A pure function, `List[Todo] => String`, with no `IO` involved. M4
 * replaces this with an aligned table.
 */
object Renderer:
  private val NoTodosMessage = "No todos yet."

  def renderList(todos: List[Todo]): String =
    if todos.isEmpty then NoTodosMessage
    else todos.map(renderOne).mkString("\n")

  private def renderOne(todo: Todo): String =
    val state = if todo.done then "done" else "pending"
    s"#${todo.id.value} [$state] ${todo.title.value}"
