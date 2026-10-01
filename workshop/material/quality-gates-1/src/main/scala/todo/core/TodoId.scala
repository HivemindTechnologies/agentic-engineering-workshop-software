package todo.core

/**
 * A todo's identity: a positive, stable number naming one row across `add`, `list` and later
 * `done`/`edit`/`remove`.
 */
opaque type TodoId = Int

object TodoId:
  def apply(value: Int): TodoId = value

  extension (id: TodoId) def value: Int = id
