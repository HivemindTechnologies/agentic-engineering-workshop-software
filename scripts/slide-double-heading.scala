//> using scala 3.3.4

/** Fail when a reveal-md vertical/horizontal slide has more than one title heading.

  Title headings are ATX `#` / `##` outside fenced code. Deeper `###+` and
  headings inside ``` fences (e.g. tocmd outlines) are ignored.

  Usage:
    slide-double-heading <path.md|directory>...
*/
import java.nio.charset.StandardCharsets
import java.nio.file.{Files, Path, Paths}
import scala.jdk.CollectionConverters.*
import scala.util.matching.Regex

val Separator: Regex = """^-{3,4}\s*$""".r
val TitleHeading: Regex = """^#{1,2} .+""".r

case class Finding(path: Path, slide: Int, headings: List[String])

def markdownPaths(path: Path): List[Path] =
  if !Files.exists(path) then Nil
  else if Files.isDirectory(path) then
    Files
      .list(path)
      .iterator()
      .asScala
      .filter(p => Files.isRegularFile(p) && p.getFileName.toString.endsWith(".md"))
      .toList
      .sortBy(_.getFileName.toString)
  else if Files.isRegularFile(path) then List(path)
  else Nil

def splitSlides(text: String): List[String] =
  val lines = text.split("\n", -1).toList
  val buf = scala.collection.mutable.ListBuffer.empty[String]
  val cur = scala.collection.mutable.ListBuffer.empty[String]
  def flush(): Unit =
    buf += cur.mkString("\n")
    cur.clear()
  lines.foreach { line =>
    if Separator.matches(line) then flush()
    else cur += line
  }
  flush()
  buf.toList

def titleHeadings(slide: String): List[String] =
  var inFence = false
  slide
    .split("\n", -1)
    .toList
    .flatMap { line =>
      if line.startsWith("```") then
        inFence = !inFence
        Nil
      else if !inFence && TitleHeading.matches(line) then List(line)
      else Nil
    }

def findings(path: Path): List[Finding] =
  val text =
    try Files.readString(path, StandardCharsets.UTF_8)
    catch case _: Exception => return Nil
  splitSlides(text).zipWithIndex.flatMap { (slide, idx) =>
    val titles = titleHeadings(slide)
    if titles.length > 1 then List(Finding(path, idx + 1, titles))
    else Nil
  }

@main def slideDoubleHeading(args: String*): Unit =
  if args.isEmpty then
    System.err.println("usage: slide-double-heading <path.md|directory>...")
    sys.exit(1)
  val targets = args.toList.flatMap(a => markdownPaths(Paths.get(a))).distinct
  if targets.isEmpty then
    System.err.println("slide-double-heading: no markdown files")
    sys.exit(1)
  val bad = targets.flatMap(findings)
  if bad.isEmpty then
    println("slide-double-heading ok")
    sys.exit(0)
  System.err.println("slide-double-heading FAILED: more than one #/## title per slide")
  bad.foreach { f =>
    System.err.println(s"${f.path}: slide ${f.slide}: ${f.headings.length} title headings")
    f.headings.foreach(h => System.err.println(s"  $h"))
  }
  sys.exit(1)
