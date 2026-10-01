package todo.store

import org.virtuslab.yaml.*

import todo.core.Todo

/**
 * The YAML wire format for a stored todo. Deliberately a plain, unvalidated data class — the
 * domain's [[Todo]] carries the validated `Title`; this type is only the shape written to and read
 * from disk, so a derived codec can never bypass the domain's smart constructors.
 */
final private[store] case class TodoRecord(id: Int, title: String, done: Boolean) derives YamlCodec

private[store] object TodoRecord:
  def from(todo: Todo): TodoRecord = TodoRecord(todo.id.value, todo.title.value, todo.done)
