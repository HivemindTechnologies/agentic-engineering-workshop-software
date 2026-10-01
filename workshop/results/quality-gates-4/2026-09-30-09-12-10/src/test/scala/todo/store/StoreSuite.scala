package todo.store

import cats.effect.IO
import munit.CatsEffectSuite

import java.nio.file.{Files, Path}
import todo.core.{Title, Todo, TodoId}

class StoreSuite extends CatsEffectSuite:
  /** A path in a real temp directory that does not (yet) exist. */
  private def freshPath(): IO[Path] =
    IO.blocking(Files.createTempFile("todos", ".yaml")).flatTap(p => IO.blocking(Files.delete(p)))

  test("reading a store path that does not exist yields an empty todo list") {
    for
      path <- freshPath()
      result <- Store.read(path)
    yield assertEquals(result, Right(Nil))
  }

  test("writing todos and reading them back yields an equal list") {
    val todos = List(
      Todo(TodoId(1), Title("Buy milk").toOption.get, done = false),
      Todo(TodoId(2), Title("Walk dog").toOption.get, done = true)
    )
    for
      path <- freshPath()
      _ <- Store.write(path, todos)
      result <- Store.read(path)
    yield assertEquals(result, Right(todos))
  }

  test("writing an empty todo list and reading it back yields an empty list") {
    for
      path <- freshPath()
      _ <- Store.write(path, Nil)
      result <- Store.read(path)
    yield assertEquals(result, Right(Nil))
  }

  test("reading a malformed YAML store file fails fast with a descriptive error") {
    for
      path <- freshPath()
      _ <- IO.blocking(Files.writeString(path, "this is not a list of todos"))
      result <- Store.read(path)
    yield result match
      case Left(err) => assert(err.message.nonEmpty)
      case Right(_)  => fail("expected malformed content to fail, not parse")
  }
