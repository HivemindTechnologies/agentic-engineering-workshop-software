package todo.core

import org.scalacheck.Gen
import org.scalacheck.Prop.forAll

class TodosPropertySuite extends munit.ScalaCheckSuite:
  // Alphanumeric and non-empty, so it can never be blank.
  private val nonBlankTitle: Gen[String] = Gen.nonEmptyListOf(Gen.alphaNumChar).map(_.mkString)

  property("adding a non-blank title always assigns an id past every existing one") {
    forAll(Gen.listOf(nonBlankTitle), nonBlankTitle) { (existingTitles, newTitle) =>
      val existing = existingTitles.zipWithIndex.map { (t, i) =>
        Todo(TodoId(i + 1), Title(t).toOption.get, done = false)
      }
      val (created, updated) = Todos.add(existing, newTitle).toOption.get
      created.id.value > existing.map(_.id.value).maxOption.getOrElse(0) &&
      updated == existing :+ created
    }
  }
