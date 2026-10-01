package todo.store

import org.virtuslab.yaml.*

import todo.core.*

/**
 * YAML wire format. Optional planning fields default when absent so older store files still load.
 */
final private[todo] case class TodoRecord(
    id: Int,
    title: String,
    done: Boolean,
    due: Option[String] = None,
    priority: Option[String] = None,
    tags: List[String] = Nil,
    assignees: List[String] = Nil,
    assigner: Option[String] = None
) derives YamlCodec

private[todo] object TodoRecord:
  def from(todo: Todo): TodoRecord =
    TodoRecord(
      id = todo.id.value,
      title = todo.title.value,
      done = todo.done,
      due = todo.due.map(_.value.toString),
      priority = todo.priority.map(Priority.render),
      tags = todo.tags.map(_.value),
      assignees = todo.assignees.map(_.value),
      assigner = todo.assigner.map(_.value)
    )
