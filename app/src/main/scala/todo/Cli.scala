package todo

import cats.effect.{ExitCode, IO}

import java.io.PrintStream
import java.nio.file.Path
import todo.core.{Title, Todo, Todos}
import todo.render.Renderer
import todo.store.Store

enum OutputFormat:
  case Table, Yaml, Json, Markdown

object OutputFormat:
  val choices: List[String] = List("table", "json", "markdown", "yaml")

  def parse(raw: String, flag: String = "--format"): Either[String, OutputFormat] =
    raw.toLowerCase match
      case "table"    => Right(OutputFormat.Table)
      case "yaml"     => Right(OutputFormat.Yaml)
      case "json"     => Right(OutputFormat.Json)
      case "markdown" => Right(OutputFormat.Markdown)
      case other =>
        Left(s"invalid $flag=$other; valid choices: ${choices.mkString(", ")}")

enum Command:
  case Greet
  case Add(title: String, meta: Todos.Meta)
  case ListTodos(
      format: OutputFormat,
      tag: Option[String],
      assignee: Option[String],
      priority: Option[String]
  )
  case Done(id: Int)
  case Edit(id: Int, title: Option[String], meta: Todos.Meta)
  case Remove(id: Int)
  case Unknown(args: List[String])
  case BadUsage(message: String)

object Cli:
  def parse(args: List[String], defaultFormat: OutputFormat = OutputFormat.Table): Command =
    args match
      case Nil                   => Command.Greet
      case "add" :: rest         => parseAdd(rest)
      case "list" :: rest        => parseList(rest, defaultFormat)
      case "done" :: id :: Nil   => parseId(id, Command.Done.apply, "done")
      case "edit" :: id :: rest  => parseEdit(id, rest)
      case "remove" :: id :: Nil => parseId(id, Command.Remove.apply, "remove")
      case other                 => Command.Unknown(other)

  private def parseAdd(rest: List[String]): Command =
    rest match
      case title :: flags if !title.startsWith("--") =>
        parseMeta(flags) match
          case Left(msg)   => Command.BadUsage(msg)
          case Right(meta) => Command.Add(title, meta)
      case _ =>
        Command.BadUsage(
          "add: expected title then optional --due/--priority/--tag/--assignee/--assigner"
        )

  private def parseEdit(idRaw: String, rest: List[String]): Command =
    idRaw.toIntOption match
      case None => Command.BadUsage(s"edit: id must be an integer, got '$idRaw'")
      case Some(id) =>
        val (title, flags) = rest match
          case t :: more if !t.startsWith("--") => (Some(t), more)
          case more                             => (None, more)
        parseMeta(flags) match
          case Left(msg)   => Command.BadUsage(msg)
          case Right(meta) => Command.Edit(id, title, meta)

  private def parseList(rest: List[String], defaultFormat: OutputFormat): Command =
    var format = defaultFormat
    var tag: Option[String] = None
    var assignee: Option[String] = None
    var priority: Option[String] = None
    var err: Option[String] = None
    rest.foreach {
      case s"--format=$v" =>
        OutputFormat.parse(v, "--format") match
          case Right(f) => format = f
          case Left(m)  => err = Some(m)
      case s"--output=$v" =>
        OutputFormat.parse(v, "--output") match
          case Right(f) => format = f
          case Left(m)  => err = Some(m)
      case s"--tag=$v"      => tag = Some(v)
      case s"--assignee=$v" => assignee = Some(v)
      case s"--priority=$v" => priority = Some(v)
      case other            => err = Some(s"Unknown list flag: $other")
    }
    err match
      case Some(m) => Command.BadUsage(m)
      case None    => Command.ListTodos(format, tag, assignee, priority)

  private def parseMeta(flags: List[String]): Either[String, Todos.Meta] =
    var due: Option[String] = None
    var clearDue = false
    var priority: Option[String] = None
    var clearPriority = false
    var tags: List[String] = Nil
    var sawTags = false
    var assignees: List[String] = Nil
    var sawAssignees = false
    var assigner: Option[String] = None
    var clearAssigner = false
    var err: Option[String] = None
    flags.foreach {
      case s"--due=$v"         => due = Some(v)
      case "--clear-due"       => clearDue = true
      case s"--priority=$v"    => priority = Some(v)
      case "--clear-priority"  => clearPriority = true
      case s"--tag=$v"         => sawTags = true; tags = tags :+ v
      case "--clear-tags"      => sawTags = true; tags = Nil
      case s"--assignee=$v"    => sawAssignees = true; assignees = assignees :+ v
      case "--clear-assignees" => sawAssignees = true; assignees = Nil
      case s"--assigner=$v"    => assigner = Some(v)
      case "--clear-assigner"  => clearAssigner = true
      case other               => err = Some(s"Unknown flag: $other")
    }
    err match
      case Some(m) => Left(m)
      case None =>
        Right(
          Todos.Meta(
            due = due,
            clearDue = clearDue,
            priority = priority,
            clearPriority = clearPriority,
            tags = if sawTags then Some(tags) else None,
            assignees = if sawAssignees then Some(assignees) else None,
            assigner = assigner,
            clearAssigner = clearAssigner
          )
        )

  private def parseId(raw: String, ctor: Int => Command, verb: String): Command =
    raw.toIntOption match
      case Some(id) => ctor(id)
      case None     => Command.BadUsage(s"$verb: id must be an integer, got '$raw'")

  def colorEnabled(noColor: Boolean, stdoutIsTty: Boolean): Boolean =
    !noColor && stdoutIsTty

  def greet(out: PrintStream): IO[Unit] = IO.blocking(out.println(Greeting.message))

  def run(
      args: List[String],
      storePath: Path,
      out: PrintStream,
      color: Boolean = false,
      defaultFormat: OutputFormat = OutputFormat.Table,
      defaultAssigner: Option[String] = None
  ): IO[ExitCode] =
    parse(args, defaultFormat) match
      case Command.Greet => greet(out).as(ExitCode.Success)
      case Command.Add(title, meta) =>
        runAdd(storePath, title, meta, defaultAssigner, out)
      case Command.ListTodos(format, tag, assignee, priority) =>
        runList(storePath, out, format, color, tag, assignee, priority)
      case Command.Done(id) =>
        runMutate(storePath, out, Todos.markDone(_, id), s"Marked #$id done")
      case Command.Edit(id, title, meta) =>
        runMutate(
          storePath,
          out,
          Todos.edit(_, id, title, meta, defaultAssigner),
          s"Edited #$id"
        )
      case Command.Remove(id) =>
        runMutate(storePath, out, Todos.remove(_, id), s"Removed #$id")
      case Command.BadUsage(message) => IO.blocking(out.println(message)).as(ExitCode.Error)
      case Command.Unknown(other) =>
        IO.blocking(out.println(s"Unknown command: ${other.mkString(" ")}")).as(ExitCode.Error)

  private def runAdd(
      path: Path,
      rawTitle: String,
      meta: Todos.Meta,
      defaultAssigner: Option[String],
      out: PrintStream
  ): IO[ExitCode] =
    withStore(path, out) { existing =>
      Todos.add(existing, rawTitle, meta, defaultAssigner) match
        case Left(err) =>
          IO.blocking(out.println(s"Could not add todo: ${describe(err)}")).as(ExitCode.Error)
        case Right((created, updated)) =>
          Store.write(path, updated) *>
            IO.blocking(
              out.println(s"Added todo #${created.id.value}: ${created.title.value}")
            ).as(ExitCode.Success)
    }

  private def runList(
      path: Path,
      out: PrintStream,
      format: OutputFormat,
      color: Boolean,
      tag: Option[String],
      assignee: Option[String],
      priority: Option[String]
  ): IO[ExitCode] =
    withStore(path, out) { todos =>
      Todos.filter(todos, tag, assignee, priority) match
        case Left(err) =>
          IO.blocking(out.println(describe(err))).as(ExitCode.Error)
        case Right(filtered) =>
          val rendered = format match
            case OutputFormat.Table    => Renderer.renderTable(filtered, color)
            case OutputFormat.Yaml     => Renderer.renderYaml(filtered)
            case OutputFormat.Json     => Renderer.renderJson(filtered)
            case OutputFormat.Markdown => Renderer.renderMarkdown(filtered)
          IO.blocking(out.println(rendered)).as(ExitCode.Success)
    }

  private def runMutate(
      path: Path,
      out: PrintStream,
      op: List[Todo] => Either[Todos.Error, List[Todo]],
      okMessage: String
  ): IO[ExitCode] =
    withStore(path, out) { existing =>
      op(existing) match
        case Left(err) =>
          IO.blocking(out.println(describe(err))).as(ExitCode.Error)
        case Right(updated) =>
          Store.write(path, updated) *>
            IO.blocking(out.println(okMessage)).as(ExitCode.Success)
    }

  private def withStore(path: Path, out: PrintStream)(
      use: List[Todo] => IO[ExitCode]
  ): IO[ExitCode] =
    Store.read(path).flatMap {
      case Left(err) =>
        IO.blocking(out.println(s"Could not read store: ${err.message}")).as(ExitCode.Error)
      case Right(todos) => use(todos)
    }

  private def describe(err: Todos.Error): String = err match
    case Todos.Error.InvalidTitle(Title.Error.Blank) => "title must not be blank"
    case Todos.Error.UnknownId(id)                   => s"unknown id: $id"
    case Todos.Error.InvalidField(message)           => message
