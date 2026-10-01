package todo.store

import cats.effect.IO
import org.virtuslab.yaml.*

import java.nio.file.{Files, Path}
import todo.core.{Title, Todo, TodoId}

/** Everything that can go wrong reading the store, each with a human-readable message. */
enum StoreError:
  case Malformed(details: String)
  case InvalidRecord(details: String)

  def message: String = this match
    case StoreError.Malformed(details)     => s"malformed store file: $details"
    case StoreError.InvalidRecord(details) => s"invalid todo in store: $details"

/**
 * Reads and writes the one YAML file that backs the todo list. The path is always an explicit
 * parameter — there is no hardcoded global path — so tests exercise a real temp file with no
 * mocking.
 */
object Store:
  def read(path: Path): IO[Either[StoreError, List[Todo]]] =
    IO.blocking(Files.exists(path)).flatMap { exists =>
      if !exists then IO.pure(Right(Nil))
      else IO.blocking(Files.readString(path)).map(decode)
    }

  def write(path: Path, todos: List[Todo]): IO[Unit] =
    IO.blocking {
      Option(path.getParent).foreach(Files.createDirectories(_))
      // org.virtuslab::scala-yaml renders an empty Seq as the empty string, which then fails to parse back
      // (`ComposerError: Expected YAML node, but found: StreamEnd`) — write the flow-empty
      // sequence explicitly so an empty store round-trips like any other.
      val content = if todos.isEmpty then "[]\n" else todos.map(TodoRecord.from).asYaml
      Files.writeString(path, content)
    }

  private def decode(content: String): Either[StoreError, List[Todo]] =
    content.as[List[TodoRecord]] match
      case Left(err)      => Left(StoreError.Malformed(err.msg))
      case Right(records) => toDomain(records)

  private def toDomain(records: List[TodoRecord]): Either[StoreError, List[Todo]] =
    records.foldLeft[Either[StoreError, List[Todo]]](Right(Nil)) { (acc, record) =>
      for
        todos <- acc
        title <- Title(record.title).left.map(_ =>
          StoreError.InvalidRecord(s"todo #${record.id} has a blank title")
        )
      yield todos :+ Todo(TodoId(record.id), title, record.done)
    }
