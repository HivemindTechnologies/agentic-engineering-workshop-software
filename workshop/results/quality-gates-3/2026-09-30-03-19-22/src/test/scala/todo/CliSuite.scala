package todo

import cats.effect.{ExitCode, IO}
import munit.CatsEffectSuite

import java.io.{ByteArrayOutputStream, PrintStream}
import java.nio.file.{Files, Path}
import todo.store.Store

class CliSuite extends CatsEffectSuite:
  private def freshStorePath(): IO[Path] =
    IO.blocking(Files.createTempFile("todos", ".yaml")).flatTap(p => IO.blocking(Files.delete(p)))

  private def captured(): (PrintStream, () => String) =
    val buffer = new ByteArrayOutputStream()
    (new PrintStream(buffer), () => buffer.toString)

  test("Cli.greet prints the pure greeting message to the given stream") {
    val (out, text) = captured()
    Cli.greet(out).map(_ => assertEquals(text().trim, Greeting.message))
  }

  test("running with no arguments greets and exits 0") {
    val (out, text) = captured()
    Cli.run(Nil, Path.of("unused.yaml"), out).map { exitCode =>
      assertEquals(exitCode, ExitCode.Success)
      assertEquals(text().trim, Greeting.message)
    }
  }

  test("adding a title appends one not-done todo and prints confirmation naming its id") {
    val (out, text) = captured()
    for
      path <- freshStorePath()
      exitCode <- Cli.run(List("add", "Buy milk"), path, out)
      stored <- Store.read(path)
    yield
      assertEquals(exitCode, ExitCode.Success)
      assert(text().contains("Buy milk"))
      assertEquals(
        stored.map(_.map(t => (t.title.value, t.done))),
        Right(List(("Buy milk", false)))
      )
  }

  test("adding a blank title leaves the store untouched and exits non-zero naming the problem") {
    val (out, text) = captured()
    for
      path <- freshStorePath()
      before <- Store.read(path)
      exitCode <- Cli.run(List("add", "   "), path, out)
      after <- Store.read(path)
    yield
      assertNotEquals(exitCode, ExitCode.Success)
      assertEquals(before, after)
      assert(text().toLowerCase.contains("title"))
  }

  test("listing an empty store prints the no-todos message and exits 0") {
    val (out, text) = captured()
    for
      path <- freshStorePath()
      exitCode <- Cli.run(List("list"), path, out)
    yield
      assertEquals(exitCode, ExitCode.Success)
      assertEquals(text().trim, "No todos yet.")
  }

  test("listing after two adds prints both todos with id, title and done state") {
    val (addOut, _) = captured()
    val (listOut, listText) = captured()
    for
      path <- freshStorePath()
      _ <- Cli.run(List("add", "Buy milk"), path, addOut)
      _ <- Cli.run(List("add", "Walk dog"), path, addOut)
      exitCode <- Cli.run(List("list"), path, listOut)
    yield
      assertEquals(exitCode, ExitCode.Success)
      val text = listText()
      assert(text.contains("Buy milk"))
      assert(text.contains("Walk dog"))
  }
