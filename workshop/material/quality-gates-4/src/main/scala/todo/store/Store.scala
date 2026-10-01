package todo.store

import cats.effect.IO
import org.virtuslab.yaml.*

import java.nio.file.{Files, Path}
import todo.core.*

enum StoreError:
  case Malformed(details: String)
  case InvalidRecord(details: String)

  def message: String = this match
    case StoreError.Malformed(details)     => s"malformed store file: $details"
    case StoreError.InvalidRecord(details) => s"invalid todo in store: $details"

object Store:
  def read(path: Path): IO[Either[StoreError, List[Todo]]] =
    IO.blocking(Files.exists(path)).flatMap { exists =>
      if !exists then IO.pure(Right(Nil))
      else IO.blocking(Files.readString(path)).map(decode)
    }

  def write(path: Path, todos: List[Todo]): IO[Unit] =
    IO.blocking {
      Option(path.getParent).foreach(Files.createDirectories(_))
      Files.writeString(path, encode(todos))
    }

  /**
   * Pure YAML encode used by Renderer too. Omits empty optional fields so round-trips stay clean.
   */
  def encode(todos: List[Todo]): String =
    if todos.isEmpty then "[]\n"
    else todos.map(encodeOne).mkString("\n") + "\n"

  private def encodeOne(todo: Todo): String =
    val r = TodoRecord.from(todo)
    val buf = scala.collection.mutable.ArrayBuffer[String](
      s"- id: ${r.id}",
      s"  title: ${quote(r.title)}",
      s"  done: ${r.done}"
    )
    r.due.foreach(d => buf += s"  due: $d")
    r.priority.foreach(p => buf += s"  priority: $p")
    if r.tags.nonEmpty then buf += s"  tags: [${r.tags.map(quote).mkString(", ")}]"
    if r.assignees.nonEmpty then buf += s"  assignees: [${r.assignees.map(quote).mkString(", ")}]"
    r.assigner.foreach(a => buf += s"  assigner: ${quote(a)}")
    buf.mkString("\n")

  private def quote(s: String): String =
    "\"" + s.replace("\\", "\\\\").replace("\"", "\\\"") + "\""

  private def decode(content: String): Either[StoreError, List[Todo]] =
    // Older / sparse records may omit lists; coerce bare null list fields before decoding.
    val normalized = content
      .replaceAll("(?m)^(\\s*(?:tags|assignees):)\\s*$", "$1 []")
      .replace("!!null", "null")
    normalized.as[List[TodoRecord]] match
      case Left(err)      => Left(StoreError.Malformed(err.msg))
      case Right(records) => toDomain(records)

  private def toDomain(records: List[TodoRecord]): Either[StoreError, List[Todo]] =
    records.foldLeft[Either[StoreError, List[Todo]]](Right(Nil)) { (acc, record) =>
      for
        todos <- acc
        title <- Title(record.title).left.map(_ =>
          StoreError.InvalidRecord(s"todo #${record.id} has a blank title")
        )
        due <- record.due match
          case None => Right(None)
          case Some(s) =>
            DueDate.parse(s).map(Some(_)).left.map(m => StoreError.InvalidRecord(m))
        priority <- record.priority match
          case None => Right(None)
          case Some(s) =>
            Priority.parse(s).map(Some(_)).left.map(m => StoreError.InvalidRecord(m))
        tags <- Option(record.tags)
          .getOrElse(Nil)
          .foldLeft[Either[StoreError, List[TodoTag]]](
            Right(Nil)
          ) { (a, raw) =>
            for
              ts <- a
              t <- TodoTag(raw).left.map(StoreError.InvalidRecord.apply)
            yield ts :+ t
          }
        assignees <- Option(record.assignees)
          .getOrElse(Nil)
          .foldLeft[
            Either[StoreError, List[Email]]
          ](Right(Nil)) { (a, raw) =>
            for
              es <- a
              e <- Email(raw).left.map(StoreError.InvalidRecord.apply)
            yield es :+ e
          }
        assigner <- record.assigner match
          case None | Some(null) => Right(None)
          case Some(s) =>
            Email(s).map(Some(_)).left.map(StoreError.InvalidRecord.apply)
      yield todos :+ Todo(
        TodoId(record.id),
        title,
        record.done,
        due,
        priority,
        tags,
        assignees,
        assigner
      )
    }
