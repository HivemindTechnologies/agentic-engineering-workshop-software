package todo

import cats.effect.{ExitCode, IO}

import java.io.PrintStream
import java.nio.file.Path
import todo.core.{Title, Todos}
import todo.render.Renderer
import todo.store.Store

/**
 * The parsed shape of a command line. Parsing is a pure function of `args` so it needs no fixture
 * or process to test.
 */
enum Command:
  case Greet
  case Add(title: String)
  case ListTodos
  case Unknown(args: List[String])

object Cli:
  def parse(args: List[String]): Command = args match
    case Nil                   => Command.Greet
    case "add" :: title :: Nil => Command.Add(title)
    case "list" :: Nil         => Command.ListTodos
    case other                 => Command.Unknown(other)

  /**
   * The M2 greeting, run against an explicit stream instead of the real stdout so a test can assert
   * on it with no mocking.
   */
  def greet(out: PrintStream): IO[Unit] = IO.blocking(out.println(Greeting.message))

  /**
   * The whole CLI, with the store path and output stream as explicit parameters. `Main` wires this
   * to the real file and `System.out`; tests wire it to a temp file and a captured stream.
   */
  def run(args: List[String], storePath: Path, out: PrintStream): IO[ExitCode] =
    parse(args) match
      case Command.Greet      => greet(out).as(ExitCode.Success)
      case Command.Add(title) => runAdd(storePath, title, out)
      case Command.ListTodos  => runList(storePath, out)
      case Command.Unknown(other) =>
        IO.blocking(out.println(s"Unknown command: ${other.mkString(" ")}")).as(ExitCode.Error)

  private def runAdd(path: Path, rawTitle: String, out: PrintStream): IO[ExitCode] =
    Store.read(path).flatMap {
      case Left(err) =>
        IO.blocking(out.println(s"Could not read store: ${err.message}")).as(ExitCode.Error)
      case Right(existing) =>
        Todos.add(existing, rawTitle) match
          case Left(err) =>
            IO.blocking(out.println(s"Could not add todo: ${describe(err)}")).as(ExitCode.Error)
          case Right((created, updated)) =>
            Store.write(path, updated) *>
              IO.blocking(
                out.println(s"Added todo #${created.id.value}: ${created.title.value}")
              ).as(ExitCode.Success)
    }

  private def runList(path: Path, out: PrintStream): IO[ExitCode] =
    Store.read(path).flatMap {
      case Left(err) =>
        IO.blocking(out.println(s"Could not read store: ${err.message}")).as(ExitCode.Error)
      case Right(todos) =>
        IO.blocking(out.println(Renderer.renderList(todos))).as(ExitCode.Success)
    }

  private def describe(err: Todos.Error): String = err match
    case Todos.Error.InvalidTitle(Title.Error.Blank) => "title must not be blank"
