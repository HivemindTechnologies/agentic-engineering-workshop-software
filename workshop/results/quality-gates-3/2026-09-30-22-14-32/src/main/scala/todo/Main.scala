package todo

import cats.effect.{ExitCode, IO, IOApp}

import java.nio.file.{Path, Paths}

object Main extends IOApp:
  private val storePath: Path = Paths.get("todos.yaml")

  def run(args: List[String]): IO[ExitCode] =
    Cli.run(args, storePath, System.out)
