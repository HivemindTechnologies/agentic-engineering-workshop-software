package todo.core

/** The pure domain model: an id, a validated non-blank title, and a done flag. */
final case class Todo(id: TodoId, title: Title, done: Boolean)

/** Pure operations over `List[Todo]`. No `IO` anywhere — the CLI layer wires these to the store. */
object Todos:
  enum Error:
    case InvalidTitle(reason: Title.Error)

  /**
   * Appends one new, not-done todo with the next unused id. Fails without changing anything when
   * the title is blank.
   */
  def add(existing: List[Todo], rawTitle: String): Either[Error, (Todo, List[Todo])] =
    Title(rawTitle) match
      case Left(reason) => Left(Error.InvalidTitle(reason))
      case Right(title) =>
        val created = Todo(nextId(existing), title, done = false)
        Right((created, existing :+ created))

  private def nextId(existing: List[Todo]): TodoId =
    TodoId(existing.map(_.id.value).maxOption.getOrElse(0) + 1)
