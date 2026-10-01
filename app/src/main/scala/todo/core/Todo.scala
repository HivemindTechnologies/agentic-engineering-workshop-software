package todo.core

import java.time.LocalDate
import java.time.format.DateTimeParseException

enum Priority:
  case Low, Medium, High

object Priority:
  def parse(raw: String): Either[String, Priority] = raw.toLowerCase match
    case "low"    => Right(Priority.Low)
    case "medium" => Right(Priority.Medium)
    case "high"   => Right(Priority.High)
    case other    => Left(s"priority: invalid value '$other' (low|medium|high)")

  def render(p: Priority): String = p match
    case Priority.Low    => "low"
    case Priority.Medium => "medium"
    case Priority.High   => "high"

opaque type Email = String
object Email:
  def apply(raw: String): Either[String, Email] =
    val t = raw.trim
    if t.isEmpty then Left("email: must not be blank")
    else if !t.contains("@") then Left("email: must contain '@'")
    else Right(t)
  extension (e: Email) def value: String = e

opaque type TodoTag = String
object TodoTag:
  def apply(raw: String): Either[String, TodoTag] =
    val t = raw.trim
    if t.isEmpty then Left("tags: must not be blank")
    else Right(t)
  extension (t: TodoTag) def value: String = t

final case class DueDate(value: LocalDate)
object DueDate:
  def parse(raw: String): Either[String, DueDate] =
    try Right(DueDate(LocalDate.parse(raw.trim)))
    catch case _: DateTimeParseException => Left(s"due date: invalid ISO date '$raw'")

/** Domain todo with optional planning metadata (develop_app.v4). */
final case class Todo(
    id: TodoId,
    title: Title,
    done: Boolean,
    due: Option[DueDate] = None,
    priority: Option[Priority] = None,
    tags: List[TodoTag] = Nil,
    assignees: List[Email] = Nil,
    assigner: Option[Email] = None
)
