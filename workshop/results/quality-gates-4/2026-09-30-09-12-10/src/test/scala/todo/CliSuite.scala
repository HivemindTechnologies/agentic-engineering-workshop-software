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

  test("listing after two adds prints a table with both titles") {
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
      assert(text.contains("ID"))
      assert(text.contains("Buy milk"))
      assert(text.contains("Walk dog"))
  }

  test("done edit remove mutate the store; unknown id exits non-zero") {
    val (out, text) = captured()
    for
      path <- freshStorePath()
      _ <- Cli.run(List("add", "Buy milk"), path, out)
      doneCode <- Cli.run(List("done", "1"), path, out)
      afterDone <- Store.read(path)
      editCode <- Cli.run(List("edit", "1", "Buy oat milk"), path, out)
      afterEdit <- Store.read(path)
      beforeBad <- Store.read(path)
      badCode <- Cli.run(List("done", "99"), path, out)
      afterBad <- Store.read(path)
      removeCode <- Cli.run(List("remove", "1"), path, out)
      afterRemove <- Store.read(path)
    yield
      assertEquals(doneCode, ExitCode.Success)
      assertEquals(afterDone.toOption.get.head.done, true)
      assertEquals(editCode, ExitCode.Success)
      assertEquals(afterEdit.toOption.get.head.title.value, "Buy oat milk")
      assertNotEquals(badCode, ExitCode.Success)
      assert(text().contains("99"))
      assertEquals(beforeBad, afterBad)
      assertEquals(removeCode, ExitCode.Success)
      assertEquals(afterRemove, Right(Nil))
  }

  test("list --output=yaml round-trips; invalid output fails") {
    val (addOut, _) = captured()
    val (yamlOut, yamlText) = captured()
    val (badOut, badText) = captured()
    for
      path <- freshStorePath()
      _ <- Cli.run(List("add", "Buy milk"), path, addOut)
      ok <- Cli.run(List("list", "--output=yaml"), path, yamlOut)
      bad <- Cli.run(List("list", "--output=xml"), path, badOut)
    yield
      assertEquals(ok, ExitCode.Success)
      assert(yamlText().contains("Buy milk"))
      assertNotEquals(bad, ExitCode.Success)
      assert(badText().toLowerCase.contains("yaml"))
      assert(badText().toLowerCase.contains("table"))
  }

  test("list --format=json and markdown; invalid format fails") {
    val (addOut, _) = captured()
    val (jsonOut, jsonText) = captured()
    val (mdOut, mdText) = captured()
    val (badOut, badText) = captured()
    for
      path <- freshStorePath()
      _ <- Cli.run(List("add", "Buy milk"), path, addOut)
      jsonCode <- Cli.run(List("list", "--format=json"), path, jsonOut)
      mdCode <- Cli.run(List("list", "--format=markdown"), path, mdOut)
      bad <- Cli.run(List("list", "--format=xml"), path, badOut)
    yield
      assertEquals(jsonCode, ExitCode.Success)
      assert(jsonText().contains("\"title\":\"Buy milk\""))
      assertEquals(mdCode, ExitCode.Success)
      assert(mdText().contains("|"))
      assert(mdText().contains("Buy milk"))
      assertNotEquals(bad, ExitCode.Success)
      assert(badText().contains("json"))
      assert(badText().contains("markdown"))
  }

  test("list respects defaultFormat when no flag") {
    val (addOut, _) = captured()
    val (listOut, listText) = captured()
    for
      path <- freshStorePath()
      _ <- Cli.run(List("add", "Buy milk"), path, addOut)
      code <- Cli.run(List("list"), path, listOut, defaultFormat = OutputFormat.Json)
    yield
      assertEquals(code, ExitCode.Success)
      assert(listText().contains("\"title\":\"Buy milk\""))
  }

  test("add with metadata and list --tag filter") {
    val (out, text) = captured()
    for
      path <- freshStorePath()
      add <- Cli.run(
        List(
          "add",
          "Ship",
          "--due=2026-10-01",
          "--priority=high",
          "--tag=work",
          "--assignee=a@x.com"
        ),
        path,
        out
      )
      hit <- Cli.run(List("list", "--tag=work"), path, out)
      miss <- Cli.run(List("list", "--tag=home", "--format=json"), path, out)
      stored <- Store.read(path)
    yield
      assertEquals(add, ExitCode.Success)
      assertEquals(hit, ExitCode.Success)
      assert(text().contains("Ship"))
      assertEquals(miss, ExitCode.Success)
      assert(stored.toOption.get.head.due.isDefined)
      assertEquals(stored.toOption.get.head.priority.map(todo.core.Priority.render), Some("high"))
  }
